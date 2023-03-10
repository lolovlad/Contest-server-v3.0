from pathlib import Path
from random import choices
import shutil
from string import ascii_letters, digits
from MainServer.settings import settings
import os


class PathExtend:
    def __init__(self, *args):
        dir_path = Path(Path(__file__).parent).parent
        self.__path: Path = Path(dir_path, settings.static_path, *args)

    def __str__(self):
        return str(self.__path)

    def abs_path(self) -> Path:
        return self.__path

    def str_to_path(self, path_file: str):
        self.__path = Path(path_file)

    def write_file(self, data, type_file: str = "w"):
        with open(self.__path, type_file) as file:
            file.write(data)

    def create_file(self, name_file: str = ""):
        if len(name_file) == 0:
            open(self.__path, 'w').close()
        else:
            open(Path(self.__path, name_file), 'w').close()

    def create_folder(self):
        if self.__path.suffix:
            path_folders = self.__path.parent
        else:
            path_folders = self.__path
        while not os.path.exists(path_folders):
            os.makedirs(path_folders)

    @classmethod
    def create_file_name(cls, extension: str,
                         size: int = 10,
                         start_name_file: str = "file") -> str:
        st = ascii_letters + digits
        return f"{start_name_file}_{''.join(choices(st, k=size))}.{extension}"

    @classmethod
    def create_folder_name(cls, size=10) -> str:
        st = ascii_letters + digits
        return f"{''.join(choices(st, k=size))}"

    def delete_dir(self):
        shutil.rmtree(self.__path)

    def delete_file(self):
        os.remove(self.__path)

    def move_file(self, new_path_file):
        shutil.copy2(self.__path, new_path_file.abs_path())

    def name_file(self):
        return self.__path.name

    def path_file(self):
        return self.__path.parent
