from cdislogging import get_logger

logger = get_logger("DataSimulator")

def error_process(do, msg, exc):
    if do == "log":
        logger.error(msg)
    elif do == "raise":
        raise exc(msg)
    else:
        raise NotSupported("{} is not supported".format(type))