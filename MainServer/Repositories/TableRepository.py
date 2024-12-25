from httpx import AsyncClient
from fastapi import Depends, UploadFile

from ..review_service import get_channel


from typing import List
from json import loads


class TableRepository:
    def __init__(self, client: AsyncClient = Depends(get_channel)):
        self.__client: AsyncClient = client

    async def save_table(self,
                         id_contest: int,
                         table: dict):
        request = await self.__client.post(f"table/{id_contest}/update", json=table)
