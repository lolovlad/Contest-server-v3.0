from httpx import AsyncClient

from fastapi import Depends
from ..review_service import get_channel

from ..Models.Compilations import GetCompilations

from typing import List


class CompilationsRepository:
    def __init__(self, client: AsyncClient = Depends(get_channel)):
        self.__client: AsyncClient = client

    async def get_list(self) -> List[GetCompilations]:
        response = await self.__client.get("compiler/list")
        return [GetCompilations.model_validate(compiler) for compiler in response.json()]