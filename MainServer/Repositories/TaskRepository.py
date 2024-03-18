from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from ..tables import Task, TypeTask, ContestToTask

from fastapi import Depends, UploadFile

from ..review_service import get_channel
from ..Models.Task import TaskViewUser, GetTaskSettings, TaskPost, BaseTaskSettings
from ..Models.TaskTestSettings import Test, SettingsTest
from typing import List
from uuid import uuid4

from ..async_database import get_session


class JsonTestRepository:
    def __init__(self,  client: AsyncClient = Depends(get_channel)):
        self.__client: AsyncClient = client

    async def get_first_test(self, id_task: int, type_test: str = "test", index: int = 0):
        response_settings = await self.__client.get(f"task_file_settings_test/all_settings_tests/{id_task}")
        response_chunk = await self.__client.get(f"task_file_settings_test/chunk_test/{id_task}", params={
            "type_test": type_test,
            "index": index
        })

        model_settings = [SettingsTest.model_validate(obj) for obj in response_settings.json()]
        model_chunk = [Test.model_validate(obj) for obj in response_chunk.json()["tests"]]
        return model_settings, model_chunk


class TaskRepository:
    def __init__(self,
                 client: AsyncClient = Depends(get_channel),
                 session: AsyncSession = Depends(get_session)):
        self.__session: AsyncSession = session
        self.__client: AsyncClient = client

    async def count_row(self) -> int:
        response = select(func.count(Task.id))
        result = await self.__session.execute(response)
        return result.scalars().first()

    async def get_list_task(self, offset: int, limit: int) -> list[Task]:
        response = select(Task).offset(offset).fetch(limit).order_by(Task.id)
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def get_type_task(self) -> list[TypeTask]:
        response = select(TypeTask)
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def get_list_task_view_by_id_contest(self, id_contest: int) -> List[TaskViewUser]:
        response = select(Task).where(Task.id_contest == id_contest)
        result = await self.__session.execute(response)
        return [TaskViewUser.model_validate(obj, from_attributes=True) for obj in result.scalars().all()]

    async def get_list_by_contest(self, id_contest: int) -> List[Task]:
        response = select(Task).where(id_contest == id_contest)
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def get(self, id_task: int) -> Task:
        result = await self.__session.get(Task, id_task)
        return result

    async def get_setting(self, id_task: int) -> GetTaskSettings:
        response_settings = await self.__client.get(f"settings/get_settings/{id_task}")
        json_response = response_settings.json()
        task_settings = GetTaskSettings(time_work=json_response["time_work"],
                                        size_raw=json_response["size_raw"],
                                        number_shipments=json_response["number_shipments"],
                                        type_input=json_response["type_input"],
                                        type_output=json_response["type_output"],
                                        files=json_response["name_file"]
                                        )
        return task_settings

    async def add(self, task_data: TaskPost) -> Task:
        entity = Task(uuid=uuid4(),
                      name_task=task_data.name_task,
                      description=task_data.description.encode(),
                      description_input=task_data.description_input.encode(),
                      description_output=task_data.description_output.encode(),
                      id_type_task=task_data.id_type_task,
                      complexity=task_data.complexity)
        try:
            self.__session.add(entity)
            await self.__session.commit()
            return entity
        except:
            await self.__session.rollback()

    async def add_settings(self, id_task: int, task_settings_data: BaseTaskSettings):
        response = await self.__client.post(f"settings/{id_task}", json=task_settings_data.model_dump())
        return response

    async def update_settings(self, id_task: int, task_settings_data: BaseTaskSettings):
        data = task_settings_data.model_dump()
        data["id"] = id_task
        response = await self.__client.put(f"settings/", json=data)
        return response

    async def update(self, task: Task):
        try:
            self.__session.add(task)
            await self.__session.commit()
        except:
            await self.__session.rollback()

    async def delete_settings(self, id_task: int):
        response = await self.__client.delete(f"settings/{id_task}")
        return response

    async def delete(self, id_task: int):
        entity = await self.get(id_task)
        await self.delete_settings(id_task)
        try:
            await self.__session.delete(entity)
            await self.__session.commit()
        except:
            await self.__session.rollback()

    async def get_by_uuid(self, uuid: str) -> Task:
        query = select(Task).where(Task.uuid == uuid)
        response = await self.__session.execute(query)
        return response.scalars().first()

    async def add_json_file(self, id_task: int, file: UploadFile):
        response = await self.__client.post(f"files/upload_json_file/{id_task}", files={'file': (file.filename, file.file)})
        return response

    async def add_file(self, id_task: int, file: UploadFile):
        response = await self.__client.post(f"files/upload_file/{id_task}", files={'file': (file.filename, file.file)})
        return response

    async def delete_file(self, id_task: int, filename: str):
        response = await self.__client.delete(f"files/delete_file/{id_task}/{filename}")
        return response

    async def check_task_in_contest(self, id_task: int, id_contest: int) -> bool:
        query = select(ContestToTask).where(and_(
            ContestToTask.id_task == id_task,
            ContestToTask.id_contest == id_contest
            )
        )
        response = await self.__session.execute(query)
        entity = response.scalars().one_or_none()
        return entity != None
