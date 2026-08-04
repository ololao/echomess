from fastapi import APIRouter
from .schemas import Registry

router = APIRouter()

@router.post('/registry', status_code=200)
async def registry(registry_data:Registry):
    pass
