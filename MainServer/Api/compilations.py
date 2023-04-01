from fastapi import APIRouter, Depends

from ..Models.Compilations import GetCompilations
from typing import List

from ..Services.CompilationsServices import CompilationsServices


router = APIRouter(prefix="/compilations")


@router.get("/list_compilations", response_model=List[GetCompilations])
async def get_list_compilations(service: CompilationsServices = Depends()):
    return await service.get_list()
