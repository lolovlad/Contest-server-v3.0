from fastapi import Depends, UploadFile
from typing import List
from sqlalchemy.orm import Session
from Classes.PathExtend import PathExtend

from ..Models.Task import TaskGet, TaskPost, TaskPut, FileUpload, \
    BaseTaskSettings, GetTaskSettings, TaskGetView, TypeInput, TypeTask, TaskToContest
from ..tables import Task
from ..Repositories.TaskRepository import TaskRepository
from ..Repositories.ContestRepository import ContestsRepository
from ..settings import settings


class TaskServices:
    def __init__(self,
                 repo: TaskRepository = Depends(),
                 repo_contest: ContestsRepository = Depends()):
        self.__repo: TaskRepository = repo
        self.__repo_contest: ContestsRepository = repo_contest
        self.__count_item: int = 20

    @property
    def count_item(self) -> int:
        return self.__count_item

    async def get_count_page(self) -> int:
        count_row = await self.__repo.count_row()
        i = int(count_row % self.__count_item != 0)
        return count_row // self.__count_item + i

    async def get_type_task(self) -> list[TypeTask]:
        entity = await self.__repo.get_type_task()
        return [TypeTask.model_validate(i, from_attributes=True) for i in entity]

    async def get_list_task(self, number_page: int) -> List[TaskGetView]:
        offset = (number_page - 1) * self.__count_item
        entity = await self.__repo.get_list_task(offset, self.__count_item)
        return [TaskGetView.model_validate(i, from_attributes=True) for i in entity]

    async def get_task(self, uuid: str) -> TaskGet:
        entity = await self.__repo.get_by_uuid(uuid)
        return TaskGet.model_validate(entity, from_attributes=True)

    async def add_task(self, task_data: TaskPost):
        task = await self.__repo.add(task_data)
        setting = BaseTaskSettings(time_work=1,
                                   size_raw=32,
                                   type_input=1,
                                   type_output=1,
                                   number_shipments=100)
        await self.__repo.add_settings(task.id, setting)

    #async def add_task_settings(self, task_data: BaseTaskSettings):
    #    response = await self.__repo.add_settings(task_data)

    async def update_task(self, uuid: str, task_data: TaskPut) -> Task:
        task = await self.__repo.get_by_uuid(uuid)
        for field, val in task_data:
            if field in ("description", "description_input", "description_output"):
                setattr(task, field, val.encode())
            else:
                setattr(task, field, val)
        await self.__repo.update(task)
        return task

    async def update_settings_task(self, uuid: str, task_data: BaseTaskSettings):
        task = await self.__repo.get_by_uuid(uuid)
        response = await self.__repo.update_settings(task.id, task_data)
        return response

    async def delete_task(self, uuid: str):
        entity = await self.__repo.get_by_uuid(uuid)
        await self.__repo.delete_settings(entity.id)
        await self.__repo.delete(entity.id)

    async def get_settings(self, uuid: str) -> GetTaskSettings:
        task = await self.__repo.get_by_uuid(uuid)
        response = await self.__repo.get_setting(task.id)
        return response

    async def upload_file(self, uuid: str, file: UploadFile):
        task = await self.__repo.get_by_uuid(uuid)
        response = await self.__repo.add_file(task.id, file)

    async def delete_file(self, uuid: str, name_file: str):
        task = await self.__repo.get_by_uuid(uuid)
        response = await self.__repo.delete_file(task.id, name_file)

    async def upload_json_file(self, uuid: str, file: UploadFile):
        task = await self.__repo.get_by_uuid(uuid)
        response = await self.__repo.add_json_file(task.id, file)

    async def delete_folder(self, id_task: int):
        folder_name = PathExtend(f"Task_Id_{id_task}")
        folder_name.delete_dir()

    async def get_list_task_flag_contest(self, uuid_contest: str) -> list[TaskToContest]:
        contest = await self.__repo_contest.get_contest_by_uuid(uuid_contest)
        list_task_to_contest = []
        for task in contest.tasks:
            list_task_to_contest.append(
                TaskToContest(
                    task=TaskGetView.model_validate(task, from_attributes=True),
                    in_contest=True
                )
            )

        return list_task_to_contest

    async def get_task_by_search_filed(self, search_field, count) -> list[TaskGetView]:
        data_field = search_field
        task_entity = await self.__repo.get_tasks_by_search_field(
            data_field,
            count
        )
        tasks = [TaskGetView.model_validate(entity, from_attributes=True) for entity in task_entity]
        return tasks
