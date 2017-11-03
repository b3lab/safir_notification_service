import logging


logger = logging.getLogger('safir_notification_service')
# TODO: use a configurable log file
hdlr = logging.FileHandler('/var/tmp/safir_notification_service.log')
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s '
    '[%(filename)s:%(lineno)s - %(funcName)s()] %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)


def get_logger():
    return logger
