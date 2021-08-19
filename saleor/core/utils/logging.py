import logging
from django_multitenant.utils import get_current_tenant

# Get an instance of a logger
logger = logging.getLogger('django')

def log_info(component, message=None, content=None):
    logger.info('--{component}--'.format(component=component))
    store = get_current_tenant()
    if store:
        logger.info('--Strore_Id: {store}--'.format(store=store.id))
    if message:
        logger.info(message)
    if content:
        logger.info(content)