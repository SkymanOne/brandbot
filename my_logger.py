import logging
import logging.config


def get_logger():
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('root')
    return logger
