import logging

# logging.getLogger() will return the root logger of the parent calling func
#   if it wasn't configured (no handlers) then we'll add a default console handler
def getLogger():
    logger = logging.getLogger()
    if len(logger.handlers) == 0:
        ch = logging.StreamHandler()
        formatter = logging.Formatter('[%(levelname)7s] %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        logger.setLevel(logging.DEBUG)
    return logger

