import os

from django.conf import settings

DEFAULT_EMAIL_TEMPLATES_PATH = os.path.join(
    settings.PROJECT_ROOT, "saleor/plugins/admin_email/default_email_templates"
)

STAFF_ORDER_CONFIRMATION_TEMPLATE_FIELD = "staff_order_confirmation_template"
SET_STAFF_PASSWORD_TEMPLATE_FIELD = "set_staff_password_template"
CSV_PRODUCT_EXPORT_SUCCESS_TEMPLATE_FIELD = "csv_product_export_success_template"
CSV_EXPORT_FAILED_TEMPLATE_FIELD = "csv_export_failed_template"
STAFF_PASSWORD_RESET_TEMPLATE_FIELD = "staff_password_reset_template"
ORDER_CREATED_TEMPLATE_FIELD = "order_created_template"


TEMPLATE_FIELDS = [
    STAFF_ORDER_CONFIRMATION_TEMPLATE_FIELD,
    SET_STAFF_PASSWORD_TEMPLATE_FIELD,
    CSV_PRODUCT_EXPORT_SUCCESS_TEMPLATE_FIELD,
    CSV_EXPORT_FAILED_TEMPLATE_FIELD,
    STAFF_PASSWORD_RESET_TEMPLATE_FIELD,
]

SET_STAFF_PASSWORD_DEFAULT_TEMPLATE = "set_password.html"
CSV_PRODUCT_EXPORT_SUCCESS_DEFAULT_TEMPLATE = "export_products_file.html"
CSV_EXPORT_FAILED_TEMPLATE_DEFAULT_TEMPLATE = "export_failed.html"
STAFF_ORDER_CONFIRMATION_DEFAULT_TEMPLATE = "staff_confirm_order.html"
STAFF_PASSWORD_RESET_DEFAULT_TEMPLATE = "password_reset.html"

#user
USER_PASSWORD_RESET_DEFAULT_TEMPLATE = "user_password_reset.html"
USER_PASSWORD_RESET_DEFAULT_SUBJECT = "User password reset"
ORDER_CREATED_DEFAULT_TEMPLATE = "order_created.html"
ORDER_CREATED_DEFAULT_SUBJECT = "Thanks for ordering from {{store.name}}!"
ORDER_CREATED_ADMIN_DEFAULT_TEMPLATE = "order_created_admin.html"
ORDER_CREATED_ADMIN_DEFAULT_SUBJECT = "New Order"

STAFF_ORDER_CONFIRMATION_SUBJECT_FIELD = "staff_order_confirmation_subject"
SET_STAFF_PASSWORD_SUBJECT_FIELD = "set_staff_password_subject"
CSV_PRODUCT_EXPORT_SUCCESS_SUBJECT_FIELD = "csv_product_export_success_subject"
CSV_EXPORT_FAILED_SUBJECT_FIELD = "csv_export_failed_subject"
STAFF_PASSWORD_RESET_SUBJECT_FIELD = "staff_password_reset_subject"


STAFF_ORDER_CONFIRMATION_DEFAULT_SUBJECT = "Order {{ order.id }} details"
SET_STAFF_PASSWORD_DEFAULT_SUBJECT = "Set password e-mail"
CSV_PRODUCT_EXPORT_SUCCESS_DEFAULT_SUBJECT = "Export products data"
CSV_EXPORT_FAILED_DEFAULT_SUBJECT = "Export products data"
STAFF_PASSWORD_RESET_DEFAULT_SUBJECT = "Staff password reset"


PLUGIN_ID = "mirumee.notifications.admin_email"
