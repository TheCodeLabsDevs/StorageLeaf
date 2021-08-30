from fastapi import APIRouter

from Settings import VERSION
from logic.database import Schemas

router = APIRouter(
    prefix='/general',
    tags=['general']
)


@router.get('/version',
            summary='Gets information about the server version',
            response_model=Schemas.Version)
async def version():
    return Schemas.Version(**VERSION)
