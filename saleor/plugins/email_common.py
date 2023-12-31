import logging
import operator
import os
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from email.headerregistry import Address
from typing import List, Optional
from saleor.core.utils.logging import log_info
import dateutil.parser
from django_multitenant.utils import get_current_tenant
import html2text
import i18naddress
import pybars
from babel.numbers import format_currency
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.mail.backends.smtp import EmailBackend
from django_prices.utils.locale import get_locale_data

from saleor.core.prices import quantize_price
from saleor.order.utils import formatComma

from ..product.product_images import get_thumbnail_size
from .base_plugin import ConfigurationTypeField
from .error_codes import PluginErrorCode
from .models import PluginConfiguration
from ..product import models as product_models

logger = logging.getLogger(__name__)


DEFAULT_TEMPLATE_HELP_TEXT = (
    "An HTML template built with Handlebars template language. Leave it "
    "blank if you don't want to send an email for this action. Use the "
    'default Saleor template by providing the "DEFAULT" string as a value.'
)
DEFAULT_SUBJECT_HELP_TEXT = "An email subject built with Handlebars template language."
DEFAULT_EMAIL_VALUE = "DEFAULT"
DEFAULT_EMAIL_TIMEOUT = 5


@dataclass
class EmailConfig:
    host: Optional[str] = None
    port: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    sender_name: Optional[str] = None
    sender_address: Optional[str] = None
    use_tls: bool = False
    use_ssl: bool = False


DEFAULT_EMAIL_CONFIGURATION = [
    {"name": "host", "value": None},
    {"name": "port", "value": None},
    {"name": "username", "value": None},
    {"name": "password", "value": None},
    {"name": "sender_name", "value": ""},
    {"name": "sender_address", "value": ""},
    {"name": "use_tls", "value": False},
    {"name": "use_ssl", "value": False},
]


DEFAULT_EMAIL_CONFIG_STRUCTURE = {
    "host": {
        "type": ConfigurationTypeField.STRING,
        "help_text": ("The host to use for sending email."),
        "label": "SMTP host",
    },
    "port": {
        "type": ConfigurationTypeField.STRING,
        "help_text": ("Port to use for the SMTP server."),
        "label": "SMTP port",
    },
    "username": {
        "type": ConfigurationTypeField.STRING,
        "help_text": ("Username to use for the SMTP server."),
        "label": "SMTP user",
    },
    "password": {
        "type": ConfigurationTypeField.PASSWORD,
        "help_text": ("Password to use for the SMTP server."),
        "label": "Password",
    },
    "sender_name": {
        "type": ConfigurationTypeField.STRING,
        "help_text": "Name which will be visible as 'from' name.",
        "label": "Sender name",
    },
    "sender_address": {
        "type": ConfigurationTypeField.STRING,
        "help_text": "Sender email which will be visible as 'from' email.",
        "label": "Sender email",
    },
    "use_tls": {
        "type": ConfigurationTypeField.BOOLEAN,
        "help_text": (
            "Whether to use a TLS (secure) connection when talking to the SMTP "
            "server. This is used for explicit TLS connections, generally on port "
            "587. Use TLS/Use SSL are mutually exclusive, so only set one of these"
            " settings to True."
        ),
        "label": "Use TLS",
    },
    "use_ssl": {
        "type": ConfigurationTypeField.BOOLEAN,
        "help_text": (
            "Whether to use an implicit TLS (secure) connection when talking to "
            "the SMTP server. In most email documentation this type of TLS "
            "connection is referred to as SSL. It is generally used on port 465. "
            "Use TLS/Use SSL are mutually exclusive, so only set one of these"
            " settings to True."
        ),
        "label": "Use SSL",
    },
}


def format_address(this, address, include_phone=True, inline=False, latin=False):
    address["name"] = f"{address.get('first_name', '')} {address.get('last_name', '')}"
    address["country_code"] = address["country"]
    address[
        "street_address"
    ] = f"{address.get('street_address_1','')}\n {address.get('street_address_2','')}"
    address_lines = i18naddress.format_address(address, latin).split("\n")
    phone = address.get("phone")
    if include_phone and phone:
        address_lines.append(str(phone))
    if inline is True:
        return pybars.strlist([", ".join(address_lines)])
    return pybars.strlist(["<br>".join(address_lines)])


def format_datetime(this, date, date_format=None):
    """Convert datetime to a required format."""
    date = dateutil.parser.isoparse(date)
    if date_format is None:
        date_format = "%d-%m-%Y"
    return date.strftime(date_format)


def get_product_image_thumbnail(this, size, image):
    """Use provided size to get a correct image."""
    expected_size = get_thumbnail_size(size, "thumbnail", "products", on_demand=False)
    return image["original"][expected_size]


def compare(this, val1, compare_operator, val2):
    """Compare two values based on the provided operator."""
    operators = {
        "==": operator.eq,
        "!=": operator.neg,
        "<": operator.lt,
        "<=": operator.le,
        ">=": operator.ge,
        ">": operator.gt,
    }
    if compare_operator not in operators:
        return False
    return operators[compare_operator](val1, val2)


def price(this, net_amount, gross_amount, currency, display_gross=False):
    amount = net_amount
    if display_gross:
        amount = gross_amount
    try:
        value = Decimal(amount)
    except (TypeError, InvalidOperation):
        return ""

    locale, locale_code = get_locale_data()
    pattern = locale.currency_formats.get("standard").pattern

    pattern = re.sub("(\xa4+)", '<span class="currency">\\1</span>', pattern)

    formatted_price = format_currency(
        value, currency, format=pattern, locale=locale_code
    )
    return pybars.strlist([formatted_price])


def list_product_customer(this, options, items, channel, channel_symbol):
    TWOPLACES = Decimal(10) ** -2       # same as Decimal('0.01')
    result = [u'<table class="product-table">']
    for thing in items:
        result.append(u'<tr>')
        result.append(u'<td class="td-number">')
        result.append(str(thing.quantity))
        result.append(u' x </td>')
        result.append(u'<td class="td-name">')
        result.append(thing.product_name)
        result.append(u'</td>')
        result.append(u'<td class="td-price">')
        # result.append(str((quantize_price(thing.total_price_net.amount, channel)).quantize(TWOPLACES)))
        result.append("{curency} {price}".format(
            curency=channel_symbol,
            price=  formatComma((quantize_price(thing.total_price_net.amount, channel)).quantize(TWOPLACES)) 
            # quantize_price(thing.total_price_net.amount, channel)
           
        ))

        logging.getLogger('django').info('---price----{sender_name}------'.format(sender_name=thing.total_price_net.amount) )


        result.append(u'</td>')
        result.append(u'</tr>')
        option_values = thing.option_items
        if option_values:
            for option_value in option_values:
                result.append(u'<tr>')
                result.append(u'<td class="td-option" colspan="3">')
                result.append(option_value["name"])
                result.append(u'</td>')
                result.append(u'</tr>')

            
                
    result.append(u'</table>')
    return result

def list_product_customer_admin(this, options, items, channel, channel_symbol):
    TWOPLACES = Decimal(10) ** -2       # same as Decimal('0.01')
    result = [u'']
    logging.getLogger('django').info('---line----{line}------'.format(line="heloooooooo") )

    for thing in items:
        logging.getLogger('django').info('---line----{line}------'.format(line=thing.__dict__) )
        option_values = thing.option_values.all()

        result.append(u'<tr style="font-family:Inter;">')
        result.append(u'<td align="left" style="vertical-align: top;word-break: break-word; width: 30px; padding-left:8px;">')
        result.append(u'<p style="font-family:Inter;margin: 0; font-size: 12px;line-height: 14px;font-weight: bold;white-space:no-wrap;">')
        result.append('{quantity}x'.format(quantity = str(thing.quantity)))
        result.append(u'</p>')
        result.append(u'</td>')
        
        result.append(u'<td align="left" style="word-break: break-word; min-width: 200px;">')
        result.append(u'<p style="font-family:Inter;margin: 0; font-size: 12px;line-height: 14px;font-weight: bold;">')
        product_name = thing.product_name if not thing.product_sku else '{} ({})'.format(thing.product_name,thing.product_sku)
        result.append(product_name)
        result.append(u'</p>')

        #  option 
        if option_values:
            logging.getLogger('django').info('---optionm----{sender_name}------'.format(sender_name="asdasdasd") )

            for option_value in option_values:
                result.append(u'<p style="font-family:Inter;margin: 0; font-size: 12px;line-height: 14px;font-weight: 400;">')
                result.append("{name}".format(
                    name=option_value.name,
                ))
                result.append(u'</p>')

        result.append(u'</td>')

        result.append(u'<td align="right" style="font-family:Inter;white-space:no-wrap; vertical-align: top; padding-right:8px;font-size: 12px;line-height: 14px;font-weight: bold;word-break: break-word; min-width:58px;">')
        result.append("{curency} {price}".format(
            curency=channel_symbol,
            price=  formatComma((quantize_price(thing.total_price_net.amount, channel)).quantize(TWOPLACES)) 
            # quantize_price(thing.total_price_net.amount, channel)
           
        ))
        result.append(u'</td>')
        result.append(u'</tr>')


# # product info
#         result.append(u'<div style="font-family:Ubuntu, Helvetica, Arial, sans-serif;font-size:12px;text-align:left;color:#000; display: flex">')
#         result.append(u'<p style="margin: 0; margin-right: 8px; font-size: 12px;line-height: 14px;font-weight: bold;width: 5%;">')
#         result.append('{quantity}x'.format(quantity = str(thing.quantity)))
#         result.append(u'</p>')
#         result.append(u'<div style="width:70%;">')
#         result.append(u'<p style="margin: 0; font-size: 12px;line-height: 14px;font-weight: bold;">')
#         result.append(thing.product_name)
#         result.append(u'</p>')
# #  option 
#         if option_values:
#             logging.getLogger('django').info('---optionm----{sender_name}------'.format(sender_name="asdasdasd") )

#             for option_value in option_values:
#                 result.append(u'<p style="margin: 0; font-size: 12px;line-height: 14px;font-weight: 400;">')
#                 result.append("{option} : {name} ({curency} {price})".format(
#                     option=option_value.option.name,
#                     name=option_value.name,
#                     curency=channel_symbol,
#                     price=formatComma((quantize_price(option_value.get_price_amount_by_channel(
#                         channel), channel)).quantize(TWOPLACES))
#                 ))
#                 result.append(u'</p>')
#         result.append(u'</div>')
# # price
#         result.append(u'<p style="margin: 0; font-size: 12px;line-height: 14px;font-weight: bold; text-align: right; flex: 1;width:25%;">')
#         # result.append(str((quantize_price(thing.total_price_net.amount, channel)).quantize(TWOPLACES)))
#         result.append("{curency} {price}".format(
#             curency=channel_symbol,
#             price=  formatComma((quantize_price(thing.total_price_net.amount, channel)).quantize(TWOPLACES)) 
#             # quantize_price(thing.total_price_net.amount, channel)
           
#         ))

#         logging.getLogger('django').info('---price----{sender_name}------'.format(sender_name=thing.total_price_net.amount) )

#         result.append(u'</p></div></td></tr>')
        

    return result

def get_full_address1(address, city, postal_code, apartment):
    result = ''
    if address:
        result = result + address
    # if city:
    #     result = result +","+ city
    # if postal_code:
    #     result = result +","+ postal_code
    if apartment:
        result = result +" "+ apartment
    return result

def get_full_address2(address, city, postal_code, apartment):
    result = ''
    # if address:
    #     result = result + address
    if postal_code:
        result = result + postal_code
    if city:
        result = result +", "+ city
    # if apartment:
    #     result = result +","+ apartment
    return result
def customer_list_address(this, options, items):
    result = [u'']
    dict_items = items.items()
    email = ''
    phone = ''
    company = ''
    city=''
    apartment=''
    postal_code=''
    address=''
    for key, value in dict_items:
        if key == 'street_address_1': #or key == 'city' or key == 'postal_code' or key == 'apartment':
            if value:
                address = value
        if key == 'email':
            if value:
                email = value
        if key == 'phone':
            if value:
                phone = value
        if key == 'company_name':
            if value:
                company = value
        if key == 'city':
            if value:
                city = value
        if key == 'apartment':
            if value:
                apartment = value
        if key == 'postal_code':
            if value:
                postal_code = value
    ctm_name = items.get('first_name', "") + " " + items.get('last_name', "")
    logging.getLogger('django').info('---ctm_name----{ctm_name}------'.format(ctm_name=ctm_name) )
    print(ctm_name,"=========================ctm_name")
    result.append(u'<div style="font-family:Inter;font-size:12px;line-height:14px;text-align:left;color:#000;">')
    result.append(str(ctm_name)),
    result.append(u'</div>')

    result.append(u'<div style="font-family:Inter;font-size:12px;line-height:14px;text-align:left;color:#000;">')
    result.append(get_full_address1(address,city,postal_code,apartment)),
    result.append(u'</div>')

    result.append(u'<div style="font-family:Inter;font-size:12px;line-height:14px;text-align:left;color:#000;">')
    result.append(get_full_address2(address,city,postal_code,apartment)),
    result.append(u'</div>')

    result.append(u'<div style="font-family:Inter;font-size:12px;line-height:14px;text-align:left;color:#000;">')
    result.append(email),
    result.append(u'</div>')

    result.append(u'<div style="font-family:Inter;font-size:12px;line-height:14px;text-align:left;color:#000;">')
    result.append(phone),
    result.append(u'</div>')

    if company:
        result.append(u'<div style="font-family:Inter;font-size:12px;line-height:14px;text-align:left;color:#000;">')
        result.append(company),
        result.append(u'</div>')

    for key, value in dict_items:
        logging.getLogger('django').info('---keyyyyy----{key}------'.format(key=key) )
        logging.getLogger('django').info('---valueeee----{value}------'.format(value=value) )

        # if key == 'id' or key == '_state' or key == 'last_name' or key == 'first_name' or key == 'country':
        #     continue
        # if value:
        #     result.append(u'<div style="font-family:Ubuntu, Helvetica, Arial, sans-serif;font-size:12px;line-height:14px;text-align:left;color:#000;">')
        #     result.append(str(value)),
        #     result.append(u'</div>')
    # result.append(u'</ul>')
    return result


def customer_list_address_delivery(this, options, items):
    result = [u'<ul>']
    dict_items = items.items()
    ctm_name = items.get('first_name', "") + " " + items.get('last_name', "")
    result.append(u'<li>')
    result.append(str(ctm_name)),
    result.append(u'</li>') 

    email = ''
    phone = ''
    company = ''
    city=''
    apartment=''
    postal_code=''
    address=''
    for key, value in dict_items:
        if key == 'street_address_1': #or key == 'city' or key == 'postal_code' or key == 'apartment':
            if value:
                address = value
        if key == 'email':
            if value:
                email = value
        if key == 'phone':
            if value:
                phone = value
        if key == 'company_name':
            if value:
                company = value
        if key == 'city':
            if value:
                city = value
        if key == 'apartment':
            if value:
                apartment = value
        if key == 'postal_code':
            if value:
                postal_code = value
    
    result.append(u'<li>')
    result.append(get_full_address1(address,city,postal_code,apartment)),
    result.append(u'</li>')
    result.append(u'<li>')
    result.append(get_full_address2(address,city,postal_code,apartment)),
    result.append(u'</li>')

    result.append(u'<li>')
    result.append(str(email)),
    result.append(u'</li>')

    result.append(u'<li>')
    result.append(str(phone)),
    result.append(u'</li>')

    result.append(u'<li>')
    result.append(str(company)),
    result.append(u'</li>')

    result.append(u'</ul>')
    return result


def customer_list_address_pickup(this, options, items):
    result = [u'<ul>']
    dict_items = items.items()
    ctm_name = items.get('first_name', "") + " " + items.get('last_name', "")
    result.append(u'<li>')
    result.append(str(ctm_name)),
    result.append(u'</li>')
    email = ''
    phone = ''
    company = ''
    for key, value in dict_items:
        if key == 'email':
            if value:
                email = value
        if key == 'phone':
            if value:
                phone = value
        if key == 'company_name':
            if value:
                company = value

    result.append(u'<li>')
    result.append(str(email)),
    result.append(u'</li>')

    result.append(u'<li>')
    result.append(str(phone)),
    result.append(u'</li>')

    result.append(u'<li>')
    result.append(str(company)),
    result.append(u'</li>')

    result.append(u'</ul>')

    return result


def send_email(config: EmailConfig, recipient_list, context, subject="", template_str=""):
    store = get_current_tenant()
    sender_name = '{} {}'.format(context.get("store_name"),
                                 config.sender_name) if config.sender_name else ""
    #
    logging.getLogger('django').info(
        '---sender_name----{sender_name}------'.format(sender_name=sender_name))
    sender_address = config.sender_address
    # logging.getLogger('django').info('---sender_name----{sender_name}------'.format(sender_name=sender_name))

    from_email = str(Address(sender_name, addr_spec=sender_address))
    if not config.host or not config.port or not config.username or not config.password:
        return

    email_backend = EmailBackend(
        host=config.host,
        port=config.port,
        username=config.username,
        password=config.password,
        use_ssl=config.use_ssl,
        use_tls=config.use_tls,
        timeout=DEFAULT_EMAIL_TIMEOUT,
    )
    compiler = pybars.Compiler()
    template = compiler.compile(template_str)
    subject_template = compiler.compile(subject)
    helpers = {
        "format_address": format_address,
        "price": price,
        "format_datetime": format_datetime,
        "get_product_image_thumbnail": get_product_image_thumbnail,
        "compare": compare,
        "product_customer": list_product_customer,
        "product_customer_admin": list_product_customer_admin,
        "address_customer": customer_list_address,
        "address_customer_delivery": customer_list_address_delivery,
        "address_customer_pickup": customer_list_address_pickup,

    }
    message = template(context, helpers=helpers)
    subject_message = subject_template(context, helpers)
    send_mail(
        subject_message,
        html2text.html2text(message),
        from_email,
        recipient_list,
        html_message=message,
        connection=email_backend,
    )


def validate_email_config(config: EmailConfig):
    email_backend = EmailBackend(
        host=config.host,
        port=config.port,
        username=config.username,
        password=config.password,
        use_ssl=config.use_ssl,
        use_tls=config.use_tls,
        fail_silently=False,
        timeout=DEFAULT_EMAIL_TIMEOUT,
    )
    with email_backend:
        # make sure that we have correct config. It will raise error in case when we are
        # not able to log in to email backend.
        pass


def validate_default_email_configuration(
    plugin_configuration: "PluginConfiguration", configuration: dict
):
    """Validate if provided configuration is correct."""

    if not plugin_configuration.active:
        return

    if configuration["use_tls"] and configuration["use_ssl"]:
        error_msg = (
            "Use TLS and Use SSL are mutually exclusive, so only set one of "
            "those settings to True."
        )
        raise ValidationError(
            {
                "use_ssl": ValidationError(
                    error_msg,
                    code=PluginErrorCode.INVALID.value,
                ),
                "use_tls": ValidationError(
                    error_msg,
                    code=PluginErrorCode.INVALID.value,
                ),
            }
        )
    config = EmailConfig(
        host=configuration["host"],
        port=configuration["port"],
        username=configuration["username"],
        password=configuration["password"],
        sender_name=configuration["sender_name"],
        sender_address=configuration["sender_address"],
        use_tls=configuration["use_tls"],
        use_ssl=configuration["use_ssl"],
    )
    if not config.sender_address:
        raise ValidationError(
            {
                "sender_address": ValidationError(
                    "Missing sender address value.",
                    code=PluginErrorCode.PLUGIN_MISCONFIGURED.value,
                )
            }
        )

    # try:
    #     # validate_email_config(config)
    #     print("hêrerererer")
    # except Exception as e:
    #     logger.warning("Unable to connect to email backend.", exc_info=e)
    #     error_msg = (
    #         "Unable to connect to email backend. Make sure that you provided "
    #         "correct values."
    #     )
    #     print("erorsorosrosrosor")

    #     raise ValidationError(
    #         {
    #             c: ValidationError(
    #                 error_msg, code=PluginErrorCode.PLUGIN_MISCONFIGURED.value
    #             )
    #             for c in configuration.keys()
    #         }
    #     )


def validate_format_of_provided_templates(
    plugin_configuration: "PluginConfiguration", template_fields: List[str]
):
    """Make sure that the templates provided by the user have the correct structure."""
    configuration = plugin_configuration.configuration
    configuration = {item["name"]: item["value"] for item in configuration}

    if not plugin_configuration.active:
        return
    compiler = pybars.Compiler()
    errors = {}
    for field in template_fields:
        template_str = configuration.get(field)
        if not template_str or template_str == DEFAULT_EMAIL_VALUE:
            continue
        try:
            compiler.compile(template_str)
        except pybars.PybarsError:
            errors[field] = ValidationError(
                "The provided template has an inccorect structure.",
                code=PluginErrorCode.INVALID.value,
            )
    if errors:
        raise ValidationError(errors)


def get_email_template(
    plugin_configuration: PluginConfiguration, template_field_name: str, default: str
) -> str:
    """Get email template from plugin configuration."""
    configuration = plugin_configuration.configuration
    for config_field in configuration:
        if config_field["name"] == template_field_name:
            return config_field["value"] or default
    return default


def get_email_template_or_default(
    plugin_configuration: Optional[PluginConfiguration],
    template_field_name: str,
    default_template_file_name: str,
    default_template_path: str,
):
    email_template_str = DEFAULT_EMAIL_VALUE
    if plugin_configuration:
        email_template_str = get_email_template(
            plugin_configuration=plugin_configuration,
            template_field_name=template_field_name,
            default=DEFAULT_EMAIL_VALUE,
        )
    if email_template_str == DEFAULT_EMAIL_VALUE:
        email_template_str = get_default_email_template(
            default_template_file_name, default_template_path
        )
    return email_template_str


def get_email_subject(
    plugin_configuration: Optional["PluginConfiguration"],
    subject_field_name: str,
    default: str,
) -> str:
    """Get email subject from plugin configuration."""
    if not plugin_configuration:
        return default
    configuration = plugin_configuration.configuration
    for config_field in configuration:
        if config_field["name"] == subject_field_name:
            return config_field["value"] or default
    return default


def get_default_email_template(
    template_file_name: str, default_template_path: str
) -> str:
    """Get default template."""
    default_template_path = os.path.join(default_template_path, template_file_name)
    with open(default_template_path) as f:
        template_str = f.read()
        return template_str
