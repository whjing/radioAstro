
import logging
from typing import Optional




logging.captureWarnings(True)
logger = logging.getLogger("skyload")
logger.setLevel(logging.DEBUG)
#    LOG_FORMAT = logging.Formatter("%(asctime)s|%(levelname)-8s| %(filename)s:%(lineno)s | %(message)s")
formatter = logging.Formatter(
    fmt=f"%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def setup_logger(
        verbosity: int = 0,
        filename: Optional[str] = None,
):
    if verbosity == 0:
        level = logging.WARNING
    elif verbosity == 1:
        level = logging.INFO
    elif verbosity >-2:
        level = logging.DEBUG
    # handler
    ch = logging.StreamHandler
    ch.setLevel(level)
    ch.setFormatter(formatter)

    logger.setLevel


def Logger(logname, filename):
    global logger
    
    # handler
    consoleHandler = logging.StreamHandler() 
    consoleHandler.setLevel(logging.DEBUG)
    # default logger level
    fileHandler = logging.FileHandler(filename=filename)
    fileHandler.setLevel(logging.INFO)
    # formatter
    LOG_FORMAT = logging.Formatter("%(asctime)s|%(levelname)-8s| %(filename)s:%(lineno)s | %(message)s")
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    LOG_FORMAT.datefmt = DATE_FORMAT
    # 给处理器设置格式
    consoleHandler.setFormatter(LOG_FORMAT)
    fileHandler.setFormatter(LOG_FORMAT)
    # 记录器设置处理器
    logger.addHandler(consoleHandler)
    logger.addHandler(fileHandler)
    return logger
