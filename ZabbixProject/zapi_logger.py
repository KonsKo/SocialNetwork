import logging
from logging.handlers import TimedRotatingFileHandler


logging.basicConfig(filename='zapi_log.log',
                    format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.INFO)
zapi_handler = TimedRotatingFileHandler('zapi_log.log', when='W6')
zapi_logger = logging.getLogger(__name__)
zapi_logger.addHandler(zapi_handler)