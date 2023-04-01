import grpc
from grpc.aio import Channel

from fastapi import Depends

from ..Services.protos import compiler_pb2_grpc, compiler_pb2
from ..grps_review import get_channel

from ..Models.Compilations import GetCompilations

from typing import List


class CompilationsRepository:
    def __init__(self, channel: Channel = Depends(get_channel)):
        self.__channel: Channel = channel

    async def get_list(self) -> List[GetCompilations]:
        sub = compiler_pb2_grpc.CompilerApiStub(self.__channel)
        response = await sub.GetListCompiler(compiler_pb2.GetListCompilerRequest(count=1))
        return [GetCompilations.from_orm(compiler) for compiler in response.compilers]