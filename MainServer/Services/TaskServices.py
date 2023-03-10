from fastapi import Depends, UploadFile
from typing import List
from sqlalchemy.orm import Session
from Classes.PathExtend import PathExtend

import grpc
from MainServer.Services.protos import file_pb2_grpc, file_pb2, settings_pb2_grpc, settings_pb2

from ..Models.Task import TaskGet, TaskPost, TaskPut, FileUpload, TaskSettings, TaskGetView, TypeInput
from ..tables import Task
from ..database import get_session
from ..settings import settings

import os


async def read_iterfile(file: UploadFile, id_task: int, chunk_size: int = 1024):
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
            return


class TaskServices:
    def __init__(self, session: Session = Depends(get_session)):
        self.__session = session
        self.__ip_review = f'{settings.server_review_host}:{settings.server_review_port}'

    def __get(self, id_task: int):
        return self.__session.query(Task).filter(Task.id == id_task).first()

    def get_list_task(self, id_contest: int) -> List[Task]:
        return self.__session.query(Task).filter(Task.id_contest == id_contest).all()

    def get_task(self, id_task: int) -> Task:
        return self.__get(id_task)

    async def add_task(self, task_data: TaskPost):
        task = Task(id_contest=task_data.id_contest,
                    name_task=task_data.name_task,
                    description=task_data.description.encode(),
                    description_input=task_data.description_input.encode(),
                    description_output=task_data.description_output.encode(),
                    type_task=task_data.type_task)
        self.__session.add(task)
        self.__session.commit()
        async with grpc.aio.insecure_channel(self.__ip_review) as channel:
            stub = settings_pb2_grpc.SettingsApiStub(channel)
            setting = settings_pb2.Settings(id=task.id,
                                            time_work=1,
                                            size_raw=32,
                                            type_input=1,
                                            type_output=1,
                                            number_shipments=100)
            response = await stub.SettingsPost(setting)

    async def add_task_settings(self, task_data: TaskSettings):
        async with grpc.aio.insecure_channel(self.__ip_review) as channel:
            stub = settings_pb2_grpc.SettingsApiStub(channel)
            setting = settings_pb2.Settings(id=task_data.id,
                                            time_work=task_data.time_work,
                                            size_raw=task_data.size_raw,
                                            type_input=task_data.type_input,
                                            number_shipments=task_data.number_shipments)

            response = await stub.SettingsPost(setting)
            return response.code

    async def update_task(self, task_data: TaskPut) -> Task:
        task = self.__get(task_data.id)
        for field, val in task_data:
            if field in ("description", "description_input", "description_output"):
                setattr(task, field, val.encode())
            else:
                setattr(task, field, val)
        self.__session.commit()
        return task

    async def update_settings_task(self, task_data: TaskSettings):
        async with grpc.aio.insecure_channel(self.__ip_review) as channel:
            stub = settings_pb2_grpc.SettingsApiStub(channel)
            setting = settings_pb2.Settings()
            for field, val in task_data:
                if field == "files":
                    continue
                else:
                    setattr(setting, field, val)
            response = await stub.SettingsUpdate(setting)
            return response.code

    async def delete_task(self, id_task: int) -> Task:
        task = self.__get(id_task)
        async with grpc.aio.insecure_channel(self.__ip_review) as channel:
            sub = settings_pb2_grpc.SettingsApiStub(channel)
            response = await sub.SettingsDelete(settings_pb2.GetSettingsRequest(id=id_task))
        self.__session.delete(task)
        self.__session.commit()
        return task

    async def get_settings(self, id_task: int) -> TaskSettings:
        async with grpc.aio.insecure_channel(self.__ip_review) as channel:
            sub = settings_pb2_grpc.SettingsApiStub(channel)
            response = await sub.SettingsGet(settings_pb2.GetSettingsRequest(id=id_task))
            task_settings = TaskSettings(id=id_task,
                                         time_work=response.settings.time_work,
                                         size_raw=response.settings.size_raw,
                                         number_shipments=response.settings.number_shipments,
                                         files=list(response.settings.name_file))
            task_settings.type_input = response.settings.type_input
            task_settings.type_output = response.settings.type_output
            return task_settings

    async def upload_file(self, id_task: int, file: UploadFile):
        async with grpc.aio.insecure_channel(self.__ip_review) as channel:
            stub = file_pb2_grpc.FileApiStub(channel)
            call = stub.UploadFile()
            async for request in read_iterfile(file, id_task):
                await call.write(request)
            await call.done_writing()
            response = await call
            return response.code

    async def delete_file(self, id_task: int, name_file: str):
        async with grpc.aio.insecure_channel(self.__ip_review) as channel:
            stud = file_pb2_grpc.FileApiStub(channel)

            split_data = os.path.splitext(name_file)
            filename = split_data[0]
            extension = split_data[1][1:]

            response = await stud.DeleteFile(file_pb2.MetaData(name=filename, extend=extension, id_task=id_task))
            return response.code

    async def upload_json_file(self, id_task: int, file: UploadFile):
        name_json = PathExtend.create_file_name("json", start_name_file=f"task_test_{id_task}")
        async with grpc.insecure_channel(self.__ip_review) as channel:
            stub = file_pb2_grpc.FileApiStub(channel)
            file.filename = name_json
            response = await stub.UploadFile(read_iterfile(file, id_task))
            return response.code

    async def delete_folder(self, id_task: int):
        folder_name = PathExtend(f"Task_Id_{id_task}")
        folder_name.delete_dir()