import grpc
from grpc.aio import Channel

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..tables import Task

from fastapi import Depends

from ..Services.protos import settings_pb2_grpc, settings_pb2, jsonTest_pb2_grpc, jsonTest_pb2
from ..grps_review import get_channel
from ..Models.Task import *
from ..Models.TaskTestSettings import Test, SettingsTest
from typing import List, Any

from ..async_database import get_session


class JsonTestRepository:
    def __init__(self,  channel: Channel = Depends(get_channel)):
        self.__channel: Channel = channel

    def get_first_test(self, id_task: int, type_test: str = "test", index: int = 0):
        sub = jsonTest_pb2_grpc.JsonTestApiStub(self.__channel)
        response_settings = await sub.GetAllSettingsTests(jsonTest_pb2.GetAllSettingsTestsRequest(id=id_task))
        response_chunk = await sub.GetChunkTest(jsonTest_pb2.GetChunkTestRequest(id=id_task, type_test=type_test, index=index))

        model_settings = [SettingsTest.from_orm(obj) for obj in response_settings.settings]
        model_chunk = [Test.from_orm(obj) for obj in response_settings.settings]
        return model_settings, model_chunk


class TaskRepository:
    def __init__(self,
                 channel: Channel = Depends(get_channel),
                 session: AsyncSession = Depends(get_session)):
        self.__session: AsyncSession = session
        self.__channel: Channel = channel

    async def get_list_task_view_by_id_contest(self, id_contest: int) -> List[TaskViewUser]:
        response = select(Task).where(id_contest == id_contest)
        result = await self.__session.execute(response)
        return [TaskViewUser.from_orm(obj) for obj in result.scalars().all()]

    async def get_list_by_contest(self, id_contest: int) -> List[Task]:
        response = select(Task).where(id_contest == id_contest)
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def get(self, id_task: int) -> Task:
        result = await self.__session.get(Task, id_task)
        return result

    async def get_setting(self, id_task: int) -> TaskSettings:
        sub = settings_pb2_grpc.SettingsApiStub(self.__channel)
        response_settings = await sub.SettingsGet(settings_pb2.GetSettingsRequest(id=id_task))
        task_settings = TaskSettings(id=id_task,
                                     time_work=response_settings.settings.time_work,
                                     size_raw=response_settings.settings.size_raw,
                                     number_shipments=response_settings.settings.number_shipments,
                                     type_input=response_settings.settings.type_input,
                                     type_output=response_settings.settings.type_output
                                     )
        return task_settings