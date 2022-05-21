import sys

from loguru import logger

from controller.config import LOGGING


def add_logging(debug_status: int = 20) -> None:
    """
    Enables logging depending on start parameter uvicorn

    Instead of print we use:                       #
               logger.debug('debug message')       #
               logger.info('info message')         #
               logger.warning('warn message')      #
               logger.error('error message')       #
               logger.critical('critical message') #
    The application creates two log/ file:
               1 - error level
               2 - debug level
    The information is also duplicated in the console

    Args:
        debug_status: 50 = CRITICAL
                      40 = ERROR
                      30 = WARNING
                      25 = SUCCESS
                      20 = INFO
                      10 = DEBUG
                      5  = TRACE

    Returns:
        None
    """

    logger.remove()
    DEBUG = True if debug_status < 20 else False

    if DEBUG:
        # We connect the output to TTY, level DEBUG
        logger.add(sys.stdout,
                   format=LOGGING.get("debug"),
                   level="DEBUG",
                   enqueue=True,
                   colorize=True)

        # Connect the output to a file, level DEBUG
        logger.add('log/debug.log',
                   format=LOGGING.get("debug"),
                   level="DEBUG",
                   enqueue=True,
                   colorize=True,
                   catch=True,
                   rotation="10 MB",
                   compression="zip")
    else:
        # We connect the output to TTY, level INFO
        logger.add(sys.stdout,
                   format=LOGGING.get("info"),
                   level="INFO",
                   enqueue=True,
                   colorize=True)

    # We connect the output to a file, level ERROR
    logger.add('log/error.log',
               format=LOGGING.get("error"),
               level="ERROR",
               backtrace=True,
               diagnose=True,
               enqueue=True,
               colorize=True,
               catch=True,
               rotation="10 MB",
               compression="zip")
