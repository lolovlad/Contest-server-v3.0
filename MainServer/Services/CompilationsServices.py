from fastapi import Depends
from ..Models.Compilations import GetCompilations
from ..Repositories.CompilationsRepository import CompilationsRepository
from typing import List


class CompilationsServices:
    def __init__(self, repo: CompilationsRepository = Depends()):
        self.__repo = repo

    async def get_list(self) -> List[GetCompilations]:
        list_compilations = await self.__repo.get_list()
        return list_compilations
