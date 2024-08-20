import sys
from functools import partial

from loguru import logger

# Initials
scenario = "STDOUTPUT_ONLY"    # "ALL" , "FILE_ONLY" , "STDOUTPUT_ONLY" accepted
level = "TRACE"  # "OMIT", "TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR" ("CRITICAL")

level = "TRACE"
enqueue = True

# Customization
logger.remove(None)

logger.level("OMIT", no=1, color="<light-black>", icon="_")  # Custom level for excluded log-events
if scenario in ("FILE_ONLY", "ALL"):
    logger.add("event_log.log",
               encoding="utf8",
               format="{time} | {level: <8} | {name: ^15} | {function: ^15} | {line: >3} | {message}",
               enqueue=enqueue,
               level=level)
if scenario in ("STDOUTPUT_ONLY", "ALL"):
    logger.add(sys.stdout,
               format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                      "<level>{level: <8}</level> | "
                      "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
               enqueue=enqueue,
               level=level)

# Aliases
omit = partial(logger.log, "OMIT")
trace = logger.trace
debug = logger.debug
info = logger.info
success = logger.success
warning = logger.warning
error = logger.error

# Use ALL:
# from logger import omit, trace, debug, info, success, warning, error
