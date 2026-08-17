from contextvars import ContextVar

request_id: ContextVar[str] = ContextVar('request_id', default='no request')
user_id: ContextVar[str] = ContextVar('user_id', default='no authentication')