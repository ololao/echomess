from fastapi import FastAPI

from .python_exceptions import python_exc_handler


def registrar(app: FastAPI):
    app.add_exception_handler(Exception, python_exc_handler)
