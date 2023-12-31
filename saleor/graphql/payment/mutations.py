from decimal import Decimal
from saleor.core.utils.logging import log_info
from django.conf import settings
import graphene
from django.core.exceptions import ValidationError

from ...channel.models import Channel
from ...checkout.calculations import calculate_checkout_total_with_gift_cards
from ...checkout.checkout_cleaner import clean_billing_address, clean_checkout_shipping
from ...checkout.fetch import fetch_checkout_info, fetch_checkout_lines
from ...checkout.utils import cancel_active_payments
from ...core.permissions import OrderPermissions
from ...core.utils import get_client_ip
from ...core.utils.url import validate_storefront_url
from ...payment import PaymentError, gateway
from ...payment.error_codes import PaymentErrorCode
from ...payment.utils import create_payment, is_currency_supported
from ..account.i18n import I18nMixin
from ..checkout.types import Checkout
from ..core.mutations import BaseMutation
from ..core.scalars import PositiveDecimal
from ..core.types import common as common_types
from .types import Payment, PaymentInitialized
from ...delivery.models import Delivery
from ...store.models import Store

class PaymentInput(graphene.InputObjectType):
    gateway = graphene.Field(
        graphene.String,
        description="A gateway to use with that payment.",
        required=True,
    )
    token = graphene.String(
        required=False,
        description=(
            "Client-side generated payment token, representing customer's "
            "billing data in a secure manner."
        ),
    )
    amount = PositiveDecimal(
        required=False,
        description=(
            "Total amount of the transaction, including "
            "all taxes and discounts. If no amount is provided, "
            "the checkout total will be used."
        ),
    )
    return_url = graphene.String(
        required=False,
        description=(
            "URL of a storefront view where user should be redirected after "
            "requiring additional actions. Payment with additional actions will not be "
            "finished if this field is not provided."
        ),
    )


class CheckoutPaymentCreate(BaseMutation, I18nMixin):
    checkout = graphene.Field(Checkout, description="Related checkout object.")
    payment = graphene.Field(Payment, description="A newly created payment.")

    class Arguments:
        checkout_id = graphene.ID(description="Checkout ID.", required=True)
        input = PaymentInput(
            description="Data required to create a new payment.", required=True
        )

    class Meta:
        description = "Create a new payment for given checkout."
        error_type_class = common_types.PaymentError
        error_type_field = "payment_errors"

    @classmethod
    def clean_payment_amount(cls, info, checkout_total, amount):
        log_info('Payment', '-------Payment Price Error--------')


        if amount != round(checkout_total.gross.amount, 2):
            raise ValidationError(
                {
                    "amount": ValidationError(
                        "Partial payments are not allowed, amount should be "
                        "equal checkout's total.",
                        code=PaymentErrorCode.PARTIAL_PAYMENT_NOT_ALLOWED,
                    )
                }
            )

    @classmethod
    def validate_gateway(cls, manager, gateway_id, currency):
        """Validate if given gateway can be used for this checkout.

        Check if provided gateway_id is on the list of available payment gateways.
        Gateway will be rejected if gateway_id is invalid or a gateway doesn't support
        checkout's currency.
        """
        if not is_currency_supported(currency, gateway_id, manager):
            raise ValidationError(
                {
                    "gateway": ValidationError(
                        f"The gateway {gateway_id} is not available for this checkout.",
                        code=PaymentErrorCode.NOT_SUPPORTED_GATEWAY.value,
                    )
                }
            )

    @classmethod
    def validate_token(cls, manager, gateway: str, input_data: dict, channel_slug: str):
        token = input_data.get("token")
        is_required = manager.token_is_required_as_payment_input(gateway, channel_slug)
        if not token and is_required:
            raise ValidationError(
                {
                    "token": ValidationError(
                        f"Token is required for {gateway}.",
                        code=PaymentErrorCode.REQUIRED.value,
                    ),
                }
            )

    @classmethod
    def validate_return_url(cls, input_data):
        return_url = input_data.get("return_url")
        if not return_url:
            return
        try:
            validate_storefront_url(return_url)
        except ValidationError as error:
            raise ValidationError(
                {"redirect_url": error}, code=PaymentErrorCode.INVALID
            )

    @classmethod
    def perform_mutation(cls, _root, info, checkout_id, **data):
        checkout = cls.get_node_or_error(
            info, checkout_id, only_type=Checkout, field="checkout_id"
        )
        data = data["input"]
        gateway = data["gateway"]

        manager = info.context.plugins
        cls.validate_gateway(manager, gateway, checkout.currency)
        cls.validate_return_url(data)

        lines = fetch_checkout_lines(checkout)
        checkout_info = fetch_checkout_info(
            checkout, lines, info.context.discounts, manager
        )

        cls.validate_token(
            manager, gateway, data, channel_slug=checkout_info.channel.slug
        )

        address = (
            checkout.shipping_address or checkout.billing_address
        )  # FIXME: check which address we need here
        checkout_total = calculate_checkout_total_with_gift_cards(
            manager=manager,
            checkout_info=checkout_info,
            lines=lines,
            address=address,
            discounts=info.context.discounts,
        )
        undiscount_checkout_total = checkout_total.gross.amount + checkout_info.checkout.discount.amount
        delivery_setting = Delivery.objects.all().first()
        current_strore = Store.objects.all().first()
        

        
        # implement delivery fee
        delivery_fee = 0
        min_order=0
        
        if delivery_setting and checkout.order_type == "delivery":
            delivery_fee = delivery_setting.delivery_fee
            # implement delivery fee when enable custom delivery fee
            if delivery_setting.enable_custom_delivery_fee and (checkout_info.billing_address.postal_code is not None):
                global delivery_fee_by_postal_code
                current_postal_code = (checkout_info.billing_address.postal_code)[0:4]
                delivery_areas = [] 
                delivery_areas.extend(delivery_setting.delivery_area['areas'])
                delivery_areas.sort(key=lambda area: area['from'] + area['to'])
                
                for x in delivery_areas:

                    if int(current_postal_code) >= x['from'] and int(current_postal_code) <= x['to']:
                        delivery_fee_by_postal_code = round(x["customDeliveryFee"], 2)
                        break
                delivery_fee = delivery_fee_by_postal_code

            # implement min order when enable custom delivery fee
            if delivery_setting.enable_minimum_delivery_order_value and (checkout_info.billing_address.postal_code is not None):
                global min_order_by_postal_code
                current_postal_code = (checkout_info.billing_address.postal_code)[0:4]
                delivery_areas = [] 
                delivery_areas.extend(delivery_setting.delivery_area['areas'])
                delivery_areas.sort(key=lambda area: area['from'] + area['to'])
                
                for x in delivery_areas:
                    if int(current_postal_code) >= x['from'] and int(current_postal_code) <= x['to']:
                        min_order_by_postal_code = x["customMinOrder"]
                        break
                min_order = min_order_by_postal_code if min_order_by_postal_code != "" else delivery_setting.min_order

            if min_order > undiscount_checkout_total and checkout.order_type == settings.ORDER_TYPES[0][0]:
                raise ValidationError(
                {
                    "min_order": "The subtotal must be equal or greater than {min_order}".format(min_order=min_order)
                }
            )
            if checkout.order_type == settings.ORDER_TYPES[0][0] and \
               (undiscount_checkout_total < delivery_setting.from_delivery or (undiscount_checkout_total >= delivery_setting.from_delivery and not delivery_setting.enable_for_big_order)):
                checkout_total.gross.amount = checkout_total.gross.amount + round(Decimal(delivery_fee), 2)
        
        # implement transaction fee
        transaction_fee = 0
        if current_strore.enable_transaction_fee:
            if data["gateway"] == settings.DUMMY_GATEWAY and current_strore.contant_enable and current_strore.contant_cost:
                transaction_fee = current_strore.contant_cost
            if data["gateway"] == settings.STRIPE_GATEWAY and current_strore.stripe_enable and current_strore.stripe_cost:
                transaction_fee = current_strore.stripe_cost
            checkout_total.gross.amount = checkout_total.gross.amount + round(transaction_fee, 2)

        amount = data.get("amount", checkout_total.gross.amount)
        clean_checkout_shipping(checkout_info, lines, PaymentErrorCode)
        clean_billing_address(checkout_info, PaymentErrorCode)

        if amount != round(checkout_total.gross.amount, 2):
            print("======================ERROR============================")
            print("checkout_token", checkout.pk)
            print("sub_total", undiscount_checkout_total)
            print("discount", checkout_info.checkout.discount.amount)
            print("gateway", data["gateway"])
            print("transaction_fee", transaction_fee)
            print("delivery_fee", delivery_fee)
            print("total_from_caculated", checkout_total.gross.amount)
            print("total_from_fe", amount)
            print("lines", lines)

        cls.clean_payment_amount(info, checkout_total, amount)
        extra_data = {
            "customer_user_agent": info.context.META.get("HTTP_USER_AGENT"),
        }

        cancel_active_payments(checkout)

        payment = create_payment(
            gateway=gateway,
            payment_token=data.get("token", ""),
            total=amount,
            currency=checkout.currency,
            email=checkout.get_customer_email(),
            extra_data=extra_data,
            # FIXME this is not a customer IP address. It is a client storefront ip
            customer_ip_address=get_client_ip(info.context),
            checkout=checkout,
            return_url=data.get("return_url"),
        )
        return CheckoutPaymentCreate(payment=payment, checkout=checkout)


class PaymentCapture(BaseMutation):
    payment = graphene.Field(Payment, description="Updated payment.")

    class Arguments:
        payment_id = graphene.ID(required=True, description="Payment ID.")
        amount = PositiveDecimal(description="Transaction amount.")

    class Meta:
        description = "Captures the authorized payment amount."
        permissions = (OrderPermissions.MANAGE_ORDERS,)
        error_type_class = common_types.PaymentError
        error_type_field = "payment_errors"

    @classmethod
    def perform_mutation(cls, _root, info, payment_id, amount=None):
        payment = cls.get_node_or_error(
            info, payment_id, field="payment_id", only_type=Payment
        )
        channel_slug = (
            payment.order.channel.slug
            if payment.order
            else payment.checkout.channel.slug
        )
        try:
            gateway.capture(
                payment, info.context.plugins, amount=amount, channel_slug=channel_slug
            )
            payment.refresh_from_db()
        except PaymentError as e:
            raise ValidationError(str(e), code=PaymentErrorCode.PAYMENT_ERROR)
        return PaymentCapture(payment=payment)


class PaymentRefund(PaymentCapture):
    class Meta:
        description = "Refunds the captured payment amount."
        permissions = (OrderPermissions.MANAGE_ORDERS,)
        error_type_class = common_types.PaymentError
        error_type_field = "payment_errors"

    @classmethod
    def perform_mutation(cls, _root, info, payment_id, amount=None):
        payment = cls.get_node_or_error(
            info, payment_id, field="payment_id", only_type=Payment
        )
        channel_slug = (
            payment.order.channel.slug
            if payment.order
            else payment.checkout.channel.slug
        )
        try:
            gateway.refund(
                payment, info.context.plugins, amount=amount, channel_slug=channel_slug
            )
            payment.refresh_from_db()
        except PaymentError as e:
            raise ValidationError(str(e), code=PaymentErrorCode.PAYMENT_ERROR)
        return PaymentRefund(payment=payment)


class PaymentVoid(BaseMutation):
    payment = graphene.Field(Payment, description="Updated payment.")

    class Arguments:
        payment_id = graphene.ID(required=True, description="Payment ID.")

    class Meta:
        description = "Voids the authorized payment."
        permissions = (OrderPermissions.MANAGE_ORDERS,)
        error_type_class = common_types.PaymentError
        error_type_field = "payment_errors"

    @classmethod
    def perform_mutation(cls, _root, info, payment_id):
        payment = cls.get_node_or_error(
            info, payment_id, field="payment_id", only_type=Payment
        )
        channel_slug = (
            payment.order.channel.slug
            if payment.order
            else payment.checkout.channel.slug
        )
        try:
            gateway.void(payment, info.context.plugins, channel_slug=channel_slug)
            payment.refresh_from_db()
        except PaymentError as e:
            raise ValidationError(str(e), code=PaymentErrorCode.PAYMENT_ERROR)
        return PaymentVoid(payment=payment)


class PaymentInitialize(BaseMutation):
    initialized_payment = graphene.Field(PaymentInitialized, required=False)

    class Arguments:
        gateway = graphene.String(
            description="A gateway name used to initialize the payment.",
            required=True,
        )
        channel = graphene.String(
            description="Slug of a channel for which the data should be returned.",
        )
        payment_data = graphene.JSONString(
            required=False,
            description=(
                "Client-side generated data required to initialize the payment."
            ),
        )

    class Meta:
        description = "Initializes payment process when it is required by gateway."
        error_type_class = common_types.PaymentError
        error_type_field = "payment_errors"

    @classmethod
    def validate_channel(cls, channel_slug):
        try:
            channel = Channel.objects.get(slug=channel_slug)
        except Channel.DoesNotExist:
            raise ValidationError(
                {
                    "channel": ValidationError(
                        f"Channel with '{channel_slug}' slug does not exist.",
                        code=PaymentErrorCode.NOT_FOUND.value,
                    )
                }
            )
        if not channel.is_active:
            raise ValidationError(
                {
                    "channel": ValidationError(
                        f"Channel with '{channel_slug}' is inactive.",
                        code=PaymentErrorCode.CHANNEL_INACTIVE.value,
                    )
                }
            )
        return channel

    @classmethod
    def perform_mutation(cls, _root, info, gateway, channel, payment_data):
        cls.validate_channel(channel_slug=channel)

        try:
            response = info.context.plugins.initialize_payment(
                gateway, payment_data, channel_slug=channel
            )
        except PaymentError as e:
            raise ValidationError(
                {
                    "payment_data": ValidationError(
                        str(e), code=PaymentErrorCode.INVALID.value
                    )
                }
            )
        return PaymentInitialize(initialized_payment=response)
