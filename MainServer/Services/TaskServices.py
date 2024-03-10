from fastapi import Depends, UploadFile
from typing import List
from sqlalchemy.orm import Session
from Classes.PathExtend import PathExtend

from ..Models.Task import TaskGet, TaskPost, TaskPut, FileUpload, BaseTaskSettings, GetTaskSettings, TaskGetView, TypeInput
from ..tables import Task
from ..Repositories.TaskRepository import TaskRepository
from ..settings import settings

import os


'''async def read_iterfile(file: UploadFile, id_task: int, chunk_size: int = 1024):
    split_data = os.path.splitext(file.filename)
    filename = split_data[0]
    extension = split_data[1][1:]

    yield file_pb2.UploadFileRequest(metadata=file_pb2.MetaData(name=filename, extend=extension, id_task=id_task))
    while True:
        chunk = file.file.read(chunk_size)
        if chunk:
            file_data_chunk = file_pb2.FileData(byte_chunk=chunk)
            entry_request = file_pb2.UploadFileRequest(file=file_data_chunk)
            yield entry_request
        else:
            return'''


class TaskServices:
    def __init__(self, repo: TaskRepository = Depends()):
        self.__repo: TaskRepository = repo

    async def get_list_task(self, id_contest: int) -> List[Task]:
        entity = await self.__repo.get_list_by_contest(id_contest)
        return entity

    async def get_task(self, id_task: int) -> Task:
        entity = await self.__repo.get(id_task)
        return entity

    async def add_task(self, task_data: TaskPost):
        task = await self.__repo.add(task_data)
        setting = BaseTaskSettings(id=task.id,
                                   time_work=1,
                                   size_raw=32,
                                   type_input=1,
                                   type_output=1,
                                   number_shipments=100)
        response = await self.__repo.add_settings(setting)

    async def add_task_settings(self, task_data: BaseTaskSettings):
        response = await self.__repo.add_settings(task_data)

    async def update_task(self, task_data: TaskPut) -> Task:
        task = await self.__repo.get(task_data.id)
        for field, val in task_data:
            if field in ("description", "description_input", "description_output"):
                setattr(task, field, val.encode())
            else:
                setattr(task, field, val)
        await self.__repo.update(task)
        return task

    async def update_settings_task(self, task_data: BaseTaskSettings):
        response = await self.__repo.update_settings(task_data)

    async def delete_task(self, id_task: int):
        await self.__repo.delete(id_task)

    async def get_settings(self, id_task: int) -> GetTaskSettings:
        response = await self.__repo.get_setting(id_task)
        return response

    async def upload_file(self, id_task: int, file: UploadFile):
        pass
        '''async with grpc.aio.insecure_channel(self.__ip_review) as channel:
            stub = file_pb2_grpc.FileApiStub(channel)
            call = stub.UploadFile()
            async for request in read_iterfile(file, id_task):
                await call.write(request)
            await call.done_writing()
            response = await call
            return response.code'''

    async def delete_file(self, id_task: int, name_file: str):
        pass
        ''' async with grpc.aio.insecure_channel(self.__ip_review) as channel:
            stud = file_pb2_grpc.FileApiStub(channel)

            split_data = os.path.splitext(name_file)
            filename = split_data[0]
            extension = split_data[1][1:]

            response = await stud.DeleteFile(file_pb2.MetaData(name=filename, extend=extension, id_task=id_task))
            return response.code'''

    async def upload_json_file(self, id_task: int, file: UploadFile):
        pass
        '''name_json = PathExtend.create_file_name("json", start_name_file=f"task_test_{id_task}")
        async with grpc.aio.insecure_channel(self.__ip_review) as channel:
            stub = file_pb2_grpc.FileApiStub(channel)
            file.filename = name_json
            call = stub.UploadFile()
            async for request in read_iterfile(file, id_task):
                await call.write(request)
            await call.done_writing()
            response = await call
            return response.code'''

    async def delete_folder(self, id_task: int):
        folder_name = PathExtend(f"Task_Id_{id_task}")
        folder_name.delete_dir()