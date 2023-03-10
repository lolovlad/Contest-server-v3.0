from fastapi import UploadFile, Depends
from typing import List
from Classes.PathExtend import PathExtend

from ..Services.protos import file_pb2_grpc, file_pb2

from ..database import get_session
from sqlalchemy.orm.session import Session

import shutil
import os


class FileServices:
    def __init__(self, session: Session = Depends(get_session)):
        self.__session = session
        self.__chunk_size = 1024

    def upload_file(self, id_task: int, file: UploadFile) -> None:
        split_data = os.path.splitext(file.filename)
        filename = split_data[0]
        extension = split_data[1][1:]

        metadata = file_pb2.MetaData(name=filename, extend=extension, id_task=id_task)
        print(filename, extension)
        yield file_pb2.UploadFileRequest(metadata=metadata)
        while True:
            chunk = file.file.read(self.__chunk_size)
            if chunk:
                file_data_chunk = file_pb2.FileData(byte_chunk=chunk)
                entry_request = file_pb2.UploadFileRequest(file=file_data_chunk)
                yield entry_request
            else:
                return

    def delete_file(self, id_task: int, name_file: str) -> None:
        file_name = PathExtend(f"Task_Id_{id_task}", "test", name_file)
        file_name.delete_file()

    def upload_json_file(self, id_task: int, file: UploadFile) -> None:
        name_json = PathExtend.create_file_name("json", start_name_file=f"task_test_{id_task}")

        split_data = os.path.splitext(name_json)
        filename = split_data[0]
        extension = split_data[1][1:]

        metadata = file_pb2.MetaData(name=filename, extend=extension, id_task=id_task)
        yield file_pb2.UploadFileRequest(metadata=metadata)
        while True:
            chunk = file.file.read(self.__chunk_size)
            if chunk:
                file_data_chunk = file_pb2.FileData(byte_chunk=chunk)
                entry_request = file_pb2.UploadFileRequest(file=file_data_chunk)
                yield entry_request
            else:
                return

    def delete_folder(self, id_task: int):
        folder_name = PathExtend(f"Task_Id_{id_task}")
        folder_name.delete_dir()