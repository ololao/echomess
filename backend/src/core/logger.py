import sys

from loguru import logger

from .logger_context import request_id, user_id

logger.remove()
logger.add(
    sys.stdout,
    serialize=True,
    backtrace=False, 
    diagnose=False 
)
def patcher(record):
    record["extra"]["request_id"] = request_id.get()
    record["extra"]["user_id"] = user_id.get()
logger.configure(patcher=patcher)

logr = logger
