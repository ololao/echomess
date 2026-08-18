import sys

import sentry_sdk
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
    current_request_id, current_user_id = request_id.get(), user_id.get()
    record["extra"]["request_id"] = current_request_id
    record["extra"]["user_id"] = current_user_id
    sentry_sdk.set_user({'id':current_user_id, 'request_id':current_request_id})
    sentry_sdk.add_breadcrumb(message=record['message'], level=record['level'].name)
logger.configure(patcher=patcher)

logr = logger
