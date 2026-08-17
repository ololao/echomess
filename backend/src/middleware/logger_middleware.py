

from uuid import uuid4

from src.core import request_id


class LogerMiddleware:
    def __init__(self, app):
        self.app = app
    async def __call__(self, scope, receive, send):
        if scope['type'] in ('http', 'websocket'):
            token = request_id.set(str(uuid4()))
            try:
                await self.app(scope, receive, send)
            finally:
                request_id.reset(token)
        else: # lifespan
            await self.app(scope, receive, send)