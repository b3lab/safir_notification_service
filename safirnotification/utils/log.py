import logging


logger = logging.getLogger('safirnotification')
# TODO: use a configurable log file
hdlr = logging.FileHandler('/var/log/safirnotification/safirnotification.log')
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s '
    '[%(filename)s:%(lineno)s - %(funcName)s()] %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)


def get_logger():
    return logger
