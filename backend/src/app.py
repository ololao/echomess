from fastapi import FastAPI

from .websockets import router


app = FastAPI()
app.include_router(router)
