import decimal
import json
from datetime import date
from typing import TYPE_CHECKING, Dict, Iterable, List, Optional, Tuple

import graphene
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.encoding import smart_text
from django_multitenant.utils import get_current_tenant
from prices import TaxedMoney
from prices.money import Money

from saleor.core.prices import quantize_price
from saleor.core.utils.logging import log_info
from saleor.graphql.notifications.schema import LiveNotification
from saleor.views import sio

from ..account.error_codes import AccountErrorCode
from ..account.models import User
from ..account.utils import store_user_address
from ..checkout import calculations
from ..checkout.error_codes import CheckoutErrorCode
from ..core.exceptions import InsufficientStock
from ..core.taxes import TaxError, zero_taxed_money
from ..core.tracing import traced_atomic_transaction
from ..core.utils.url import validate_storefront_url
from ..delivery.models import Delivery
from ..discount import DiscountInfo, DiscountValueType, OrderDiscountType
from ..discount.models import NotApplicable
from ..discount.utils import (add_voucher_usage_by_customer,
                              decrease_voucher_usage, increase_voucher_usage,
                              remove_voucher_usage_by_customer)
from ..graphql.checkout.utils import \
    prepare_insufficient_stock_checkout_validation_error
from ..order import OrderLineData, OrderOrigin, OrderStatus
from ..order.actions import order_created
from ..order.models import Order, OrderLine
from ..order.notifications import send_order_confirmation
from ..payment import PaymentError, gateway
from ..payment.models import Payment, Transaction
from ..payment.utils import fetch_customer_id, store_customer_id
from ..product.models import ProductTranslation, ProductVariantTranslation
from ..store.models import Store
from ..warehouse.availability import check_stock_quantity_bulk
from ..warehouse.management import allocate_stocks
from . import AddressType
from .checkout_cleaner import clean_checkout_payment, clean_checkout_shipping
from .models import Checkout
from .utils import get_voucher_for_checkout


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        super(DecimalEncoder, self).default(o)


if TYPE_CHECKING:
    from ..plugins.manager import PluginsManager
    from .fetch import CheckoutInfo, CheckoutLineInfo


def _get_voucher_data_for_order(checkout_info: "CheckoutInfo") -> dict:
    """Fetch, process and return voucher/discount data from checkout.

    Careful! It should be called inside a transaction.

    :raises NotApplicable: When the voucher is not applicable in the current checkout.
    """
    checkout = checkout_info.checkout
    voucher = get_voucher_for_checkout(checkout_info, with_lock=True)

    if checkout.voucher_code and not voucher:
        msg = "Voucher expired in meantime. Order placement aborted."
        raise NotApplicable(msg)

    if not voucher:
        return {}

    increase_voucher_usage(voucher)
    if voucher.apply_once_per_customer:
        add_voucher_usage_by_customer(voucher, checkout_info.get_customer_email())
    return {
        "voucher": voucher,
    }


def _process_shipping_data_for_order(
    checkout_info: "CheckoutInfo",
    shipping_price: TaxedMoney,
    manager: "PluginsManager",
    lines: Iterable["CheckoutLineInfo"],
) -> dict:
    """Fetch, process and return shipping data from checkout."""
    shipping_address = checkout_info.shipping_address

    if checkout_info.user and shipping_address:
        store_user_address(
            checkout_info.user, shipping_address, AddressType.SHIPPING, manager=manager
        )
        if checkout_info.user.addresses.filter(pk=shipping_address.pk).exists():
            shipping_address = shipping_address.get_copy()

    return {
        "shipping_address": shipping_address,
        "shipping_method": checkout_info.shipping_method,
        "shipping_method_name": smart_text(checkout_info.shipping_method),
        "shipping_price": shipping_price,
        "weight": checkout_info.checkout.get_total_weight(lines),
    }


def _process_user_data_for_order(checkout_info: "CheckoutInfo", manager):
    """Fetch, process and return shipping data from checkout."""
    billing_address = checkout_info.billing_address

    if checkout_info.user and billing_address:
        store_user_address(
            checkout_info.user, billing_address, AddressType.BILLING, manager=manager
        )
        if checkout_info.user.addresses.filter(pk=billing_address.pk).exists():
            billing_address = billing_address.get_copy()

    user_email = checkout_info.get_customer_email()
    return {
        "user": checkout_info.user,
        "user_email": user_email if user_email else '',
        "billing_address": billing_address,
        "customer_note": checkout_info.checkout.note,
    }


def _validate_gift_cards(checkout: Checkout):
    """Check if all gift cards assigned to checkout are available."""
    if (
        not checkout.gift_cards.count()
        == checkout.gift_cards.active(date=date.today()).count()
    ):
        msg = "Gift card has expired. Order placement cancelled."
        raise NotApplicable(msg)


def _create_line_for_order(
    manager: "PluginsManager",
    checkout_info: "CheckoutInfo",
    lines: Iterable["CheckoutLineInfo"],
    checkout_line_info: "CheckoutLineInfo",
    discounts: Iterable[DiscountInfo],
    products_translation: Dict[int, Optional[str]],
    variants_translation: Dict[int, Optional[str]],
) -> OrderLineData:
    """Create a line for the given order.

    :raises InsufficientStock: when there is not enough items in stock for this variant.
    """
    checkout_line = checkout_line_info.line
    quantity = checkout_line.quantity
    variant = checkout_line_info.variant
    product = checkout_line_info.product
    # handle product option
    option_values = checkout_line_info.line.option_values
    address = (
        checkout_info.shipping_address or checkout_info.billing_address
    )  # FIXME: check which address we need here

    product_name = str(product)
    variant_name = str(variant)

    translated_product_name = products_translation.get(product.id, "")
    translated_variant_name = variants_translation.get(variant.id, "")

    if translated_product_name == product_name:
        translated_product_name = ""

    if translated_variant_name == variant_name:
        translated_variant_name = ""

    total_line_price = manager.calculate_checkout_line_total(
        checkout_info,
        lines,
        checkout_line_info,
        address,
        discounts,
    )
    unit_price = manager.calculate_checkout_line_unit_price(
        total_line_price,
        quantity,
        checkout_info,
        lines,
        checkout_line_info,
        address,
        discounts,
    )
    tax_rate = manager.get_checkout_line_tax_rate(
        checkout_info, lines, checkout_line_info, address, discounts, unit_price
    )

    line = OrderLine(
        product_name=product_name,
        variant_name=variant_name,
        translated_product_name=translated_product_name,
        translated_variant_name=translated_variant_name,
        product_sku=variant.sku,
        is_shipping_required=variant.is_shipping_required(),
        quantity=quantity,
        variant=variant,
        unit_price=unit_price,  # type: ignore
        total_price=total_line_price,
        tax_rate=tax_rate,
    )
    line_info = OrderLineData(line=line, quantity=quantity,
                              variant=variant, option_values=option_values)

    return line_info


def _create_lines_for_order(
    manager: "PluginsManager",
    checkout_info: "CheckoutInfo",
    lines: Iterable["CheckoutLineInfo"],
    discounts: Iterable[DiscountInfo],
) -> Iterable[OrderLineData]:
    """Create a lines for the given order.

    :raises InsufficientStock: when there is not enough items in stock for this variant.
    """
    translation_language_code = checkout_info.checkout.language_code
    country_code = checkout_info.get_country()

    variants = []
    quantities = []
    products = []
    for line_info in lines:
        variants.append(line_info.variant)
        quantities.append(line_info.line.quantity)
        products.append(line_info.product)

    products_translation = ProductTranslation.objects.filter(
        product__in=products, language_code=translation_language_code
    ).values("product_id", "name")
    product_translations = {
        product_translation["product_id"]: product_translation.get("name")
        for product_translation in products_translation
    }

    variants_translation = ProductVariantTranslation.objects.filter(
        product_variant__in=variants, language_code=translation_language_code
    ).values("product_variant_id", "name")
    variants_translation = {
        variant_translation["product_variant_id"]: variant_translation.get("name")
        for variant_translation in variants_translation
    }

    check_stock_quantity_bulk(
        variants, country_code, quantities, checkout_info.channel.slug
    )

    return [
        _create_line_for_order(
            manager,
            checkout_info,
            lines,
            checkout_line_info,
            discounts,
            product_translations,
            variants_translation,
        )
        for checkout_line_info in lines
    ]


def _prepare_order_data(
    *,
    manager: "PluginsManager",
    checkout_info: "CheckoutInfo",
    lines: Iterable["CheckoutLineInfo"],
    discounts
) -> dict:
    """Run checks and return all the data from a given checkout to create an order.

    :raises NotApplicable InsufficientStock:
    """
    checkout = checkout_info.checkout
    order_data = {}
    address = (
        checkout_info.shipping_address or checkout_info.billing_address
    )  # FIXME: check which address we need here

    taxed_total = calculations.checkout_total(
        manager=manager,
        checkout_info=checkout_info,
        lines=lines,
        address=address,
        discounts=discounts,
    )
    cards_total = checkout.get_total_gift_cards_balance()
    taxed_total.gross -= cards_total
    taxed_total.net -= cards_total

    taxed_total = max(taxed_total, zero_taxed_money(checkout.currency))
    undiscounted_total = taxed_total + checkout.discount
    # implement delivery fee
    delivery_setting = Delivery.objects.all().first()
    current_strore = Store.objects.all().first()
    undiscount_checkout_total_amount = taxed_total.gross.amount + checkout.discount.amount
    if delivery_setting:
        if delivery_setting.min_order > undiscount_checkout_total_amount and checkout.order_type == settings.ORDER_TYPES[0][0]:
            raise ValidationError(
                {
                    "min_order": "The subtotal must be equal or greater than {min_order}".format(min_order=delivery_setting.min_order)
                }
            )
        if checkout.order_type == settings.ORDER_TYPES[0][0] and delivery_setting.delivery_fee and \
           (undiscount_checkout_total_amount < delivery_setting.from_delivery or (undiscount_checkout_total_amount >= delivery_setting.from_delivery and not delivery_setting.enable_for_big_order)):
            delivery_fee = Money(amount=delivery_setting.delivery_fee,
                                 currency=checkout.currency)
            taxed_total = taxed_total + TaxedMoney(net=delivery_fee, gross=delivery_fee)
            order_data["delivery_fee"] = delivery_setting.delivery_fee

    # implement transaction fee
    payment_gateway = checkout.get_last_active_payment().gateway
    if current_strore.enable_transaction_fee:
        if payment_gateway == settings.DUMMY_GATEWAY and current_strore.contant_enable and current_strore.contant_cost:
            contant_cost = Money(amount=current_strore.contant_cost,
                                 currency=checkout.currency)
            taxed_total = taxed_total + TaxedMoney(net=contant_cost, gross=contant_cost)
            order_data["transaction_cost"] = current_strore.contant_cost
        if payment_gateway == settings.STRIPE_GATEWAY and current_strore.stripe_enable and current_strore.stripe_cost:
            stripe_cost = Money(amount=current_strore.stripe_cost,
                                currency=checkout.currency)
            taxed_total = taxed_total + TaxedMoney(net=stripe_cost, gross=stripe_cost)
            order_data["transaction_cost"] = current_strore.stripe_cost

    shipping_total = manager.calculate_checkout_shipping(
        checkout_info, lines, address, discounts
    )
    shipping_tax_rate = manager.get_checkout_shipping_tax_rate(
        checkout_info, lines, address, discounts, shipping_total
    )
    order_data.update(
        _process_shipping_data_for_order(checkout_info, shipping_total, manager, lines)
    )
    order_data.update(_process_user_data_for_order(checkout_info, manager))
    order_data.update(
        {
            "language_code": checkout.language_code,
            "tracking_client_id": checkout.tracking_code or "",
            "total": taxed_total,
            "undiscounted_total": undiscounted_total,
            "shipping_tax_rate": shipping_tax_rate,
        }
    )

    order_data["lines"] = _create_lines_for_order(
        manager, checkout_info, lines, discounts
    )

    # validate checkout gift cards
    _validate_gift_cards(checkout)

    # Get voucher data (last) as they require a transaction
    order_data.update(_get_voucher_data_for_order(checkout_info))

    # assign gift cards to the order

    order_data["total_price_left"] = (
        manager.calculate_checkout_subtotal(checkout_info, lines, address, discounts)
        + shipping_total
        - checkout.discount
    ).gross

    manager.preprocess_order_creation(checkout_info, discounts, lines)
    return order_data


@traced_atomic_transaction()
def _create_order(
    *,
    checkout_info: "CheckoutInfo",
    order_data: dict,
    user: User,
    manager: "PluginsManager",
    site_settings=None
) -> Order:
    """Create an order from the checkout.

    Each order will get a private copy of both the billing and the shipping
    address (if shipping).

    If any of the addresses is new and the user is logged in the address
    will also get saved to that user's address book.

    Current user's language is saved in the order so we can later determine
    which language to use when sending email.
    """
    from ..order.utils import add_gift_card_to_order

    checkout = checkout_info.checkout
    order = Order.objects.filter(checkout_token=checkout.token).first()
    if order is not None:
        return order

    total_price_left = order_data.pop("total_price_left")
    order_lines_info = order_data.pop("lines")

    if site_settings is None:
        site_settings = Site.objects.get_current().settings

    status = (
        OrderStatus.UNFULFILLED
        if site_settings.automatically_confirm_all_new_orders
        else OrderStatus.UNCONFIRMED
    )

    order = Order.objects.create(
        **order_data,
        checkout_token=checkout.token,
        status=status,
        origin=OrderOrigin.CHECKOUT,
        channel=checkout_info.channel,
        order_type=checkout.order_type,
        expected_date=checkout.expected_date,
        expected_time=checkout.expected_time,
        table_name=checkout.table_name,
        store=checkout.store,
    )
    if checkout.discount:
        # store voucher as a fixed value as it this the simplest solution for now.
        # This will be solved when we refactor the voucher logic to use .discounts
        # relations
        order.discounts.create(
            type=OrderDiscountType.VOUCHER,
            value_type=DiscountValueType.FIXED,
            value=checkout.discount.amount,
            name=checkout.discount_name,
            translated_name=checkout.translated_discount_name,
            currency=checkout.currency,
            amount_value=checkout.discount_amount,
        )

    order_lines = []
    for line_info in order_lines_info:
        line = line_info.line
        line.order_id = order.pk
        order_lines.append(line)

    order_line_instances = OrderLine.objects.bulk_create(order_lines)

    # add option values to order line
    for order_line_instance, line_info in zip(order_line_instances, order_lines_info):
        option_values = line_info.option_values.all()
        if option_values:
            option_values_list = []
            option_values_dict_list = []
            for option_values_in_line in option_values:
                option_value_order_line = OrderLine.option_values.through(
                    optionvalue_id=option_values_in_line.id, orderline_id=order_line_instance.id)
                option_values_list.append(option_value_order_line)
                option_values_dict = {}
                option_values_dict["price"] = option_values_in_line.get_price_amount_by_channel(
                    order.channel.slug)
                option_values_dict["id"] = option_values_in_line.id
                option_values_dict["name"] = option_values_in_line.name
                option_values_dict["currency"] = order.channel.currency_code
                option_values_dict["type"] = option_values_in_line.option.type
                option_values_dict_list.append(option_values_dict)
            order_line_instance.option_items = json.dumps(
                option_values_dict_list, cls=DecimalEncoder)
            order_line_instance.save()
            order_line_instance.option_values.through.objects.bulk_create(
                option_values_list)

    country_code = checkout_info.get_country()
    allocate_stocks(order_lines_info, country_code, checkout_info.channel.slug)

    # Add gift cards to the order
    for gift_card in checkout.gift_cards.select_for_update():
        total_price_left = add_gift_card_to_order(order, gift_card, total_price_left)

    # assign checkout payments to the order
    checkout.payments.update(order=order)

    # copy metadata from the checkout into the new order
    order.metadata = checkout.metadata
    order.redirect_url = checkout.redirect_url
    order.private_metadata = checkout.private_metadata
    order.update_total_paid()
    order.save()

    transaction.on_commit(
        lambda: order_created(order=order, user=user, manager=manager)
    )

    # Send the order confirmation email
    transaction.on_commit(
        lambda: send_order_confirmation(order, checkout.redirect_url, manager)
    )

    return order


def _prepare_checkout(
    manager: "PluginsManager",
    checkout_info: "CheckoutInfo",
    lines: Iterable["CheckoutLineInfo"],
    discounts,
    tracking_code,
    redirect_url,
    payment,
):
    """Prepare checkout object to complete the checkout process."""
    checkout = checkout_info.checkout
    clean_checkout_shipping(checkout_info, lines, CheckoutErrorCode)
    clean_checkout_payment(
        manager,
        checkout_info,
        lines,
        discounts,
        CheckoutErrorCode,
        last_payment=payment,
    )
    if not checkout_info.channel.is_active:
        raise ValidationError(
            {
                "channel": ValidationError(
                    "Cannot complete checkout with inactive channel.",
                    code=CheckoutErrorCode.CHANNEL_INACTIVE.value,
                )
            }
        )
    if redirect_url:
        try:
            validate_storefront_url(redirect_url)
        except ValidationError as error:
            raise ValidationError(
                {"redirect_url": error}, code=AccountErrorCode.INVALID.value
            )

    to_update = []
    if redirect_url and redirect_url != checkout.redirect_url:
        checkout.redirect_url = redirect_url
        to_update.append("redirect_url")

    if tracking_code and tracking_code != checkout.tracking_code:
        checkout.tracking_code = tracking_code
        to_update.append("tracking_code")

    if to_update:
        to_update.append("last_change")
        checkout.save(update_fields=to_update)


def release_voucher_usage(order_data: dict):
    voucher = order_data.get("voucher")
    if voucher:
        decrease_voucher_usage(voucher)
        if "user_email" in order_data:
            remove_voucher_usage_by_customer(voucher, order_data["user_email"])


def _get_order_data(
    manager: "PluginsManager",
    checkout_info: "CheckoutInfo",
    lines: Iterable["CheckoutLineInfo"],
    discounts: List[DiscountInfo],
) -> dict:
    """Prepare data that will be converted to order and its lines."""
    try:
        order_data = _prepare_order_data(
            manager=manager,
            checkout_info=checkout_info,
            lines=lines,
            discounts=discounts,
        )
    except InsufficientStock as e:
        error = prepare_insufficient_stock_checkout_validation_error(e)
        raise error
    except NotApplicable:
        raise ValidationError(
            "Voucher not applicable",
            code=CheckoutErrorCode.VOUCHER_NOT_APPLICABLE.value,
        )
    except TaxError as tax_error:
        raise ValidationError(
            "Unable to calculate taxes - %s" % str(tax_error),
            code=CheckoutErrorCode.TAX_ERROR.value,
        )
    return order_data


def _process_payment(
    payment: Payment,
    customer_id: Optional[str],
    store_source: bool,
    payment_data: Optional[dict],
    order_data: dict,
    manager: "PluginsManager",
    channel_slug: str,
    checkout: Checkout = None
) -> Transaction:
    """Process the payment assigned to checkout."""
    try:
        if payment.to_confirm:
            txn = gateway.confirm(
                payment,
                manager,
                additional_data=payment_data,
                channel_slug=channel_slug,
            )
        else:
            txn = gateway.process_payment(
                payment=payment,
                token=payment.token,
                manager=manager,
                customer_id=customer_id,
                store_source=store_source,
                additional_data=payment_data,
                channel_slug=channel_slug,
                checkout=checkout
            )
        payment.refresh_from_db()
        if not txn.is_success:
            raise PaymentError(txn.error)
    except PaymentError as e:
        release_voucher_usage(order_data)
        raise ValidationError(str(e), code=CheckoutErrorCode.PAYMENT_ERROR.value)
    return txn


def complete_checkout(
    manager: "PluginsManager",
    checkout_info: "CheckoutInfo",
    lines: Iterable["CheckoutLineInfo"],
    payment_data,
    store_source,
    discounts,
    user,
    site_settings=None,
    tracking_code=None,
    redirect_url=None,
    txn: "dict" = None
) -> Tuple[Optional[Order], bool, dict]:
    """Logic required to finalize the checkout and convert it to order.

    Should be used with transaction_with_commit_on_errors, as there is a possibility
    for thread race.
    :raises ValidationError
    """
    checkout = checkout_info.checkout
    channel_slug = checkout_info.channel.slug
    payment = checkout.get_last_active_payment()
    _prepare_checkout(
        manager=manager,
        checkout_info=checkout_info,
        lines=lines,
        discounts=discounts,
        tracking_code=tracking_code,
        redirect_url=redirect_url,
        payment=payment,
    )

    try:
        order_data = _get_order_data(manager, checkout_info, lines, discounts)
    except ValidationError as exc:
        gateway.payment_refund_or_void(payment, manager, channel_slug=channel_slug)
        raise exc

    customer_id = None
    if store_source and payment:
        customer_id = fetch_customer_id(user=user, gateway=payment.gateway)
    if txn is None:
        txn = _process_payment(
            payment=payment,  # type: ignore
            customer_id=customer_id,
            store_source=store_source,
            payment_data=payment_data,
            order_data=order_data,
            manager=manager,
            channel_slug=channel_slug,
            checkout=checkout
        )
    if txn.customer_id and user.is_authenticated:
        store_customer_id(user, payment.gateway, txn.customer_id)  # type: ignore

    action_required = txn.action_required
    action_data = txn.action_required_data if action_required else {}

    order = None
    if not action_required:
        try:
            order = _create_order(
                checkout_info=checkout_info,
                order_data=order_data,
                user=user,  # type: ignore
                manager=manager,
                site_settings=site_settings,
            )
            # remove checkout after order is successfully created
            checkout.delete()
            store = get_current_tenant()

            if order:
                # emit event create
                print("-------store----------")
                print(store.id)
                print("-------order store id----------")
                print(order.store_id)
                LiveNotification.new_message(
                    graphene.Node.to_global_id("Store", order.store_id),
                    graphene.Node.to_global_id("Order", order.id))
                
            # write log
            log_info('Order', 'Order', content={
                "order": order.__dict__,
                "address": vars(order.billing_address)})
        except InsufficientStock as e:
            release_voucher_usage(order_data)
            gateway.payment_refund_or_void(payment, manager, channel_slug=channel_slug)
            error = prepare_insufficient_stock_checkout_validation_error(e)
            raise error

    return order, action_required, action_data, checkout.redirect_url
