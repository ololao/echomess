from fastapi import APIRouter

from .codes import code_router
from .google import google_router
from .jwt import jwt_router
from .urls import url_router

auth_router = APIRouter(prefix="/auth")
auth_router.include_router(code_router)
auth_router.include_router(url_router)
auth_router.include_router(jwt_router)
auth_router.include_router(google_router)
