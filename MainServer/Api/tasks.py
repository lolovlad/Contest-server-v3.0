from fastapi import APIRouter, Depends, File, UploadFile, status, UploadFile

from fastapi.responses import JSONResponse

from ..Models.User import UserGet, TypeUser
from ..Services.LoginServices import get_current_user
from ..Services.TaskServices import TaskServices
from ..Services.FileServices import FileServices
from ..Models.Task import TaskGet, TaskSettings, TaskPut, TaskPost, TaskGetView

from typing import List


router = APIRouter(prefix="/tasks")


@router.post("/", responses={status.HTTP_200_OK: {"message": "ok"}})
async def post_task(task_data: TaskPost, task_services: TaskServices = Depends(),
                    user: UserGet = Depends(get_current_user)):
    if user.type == TypeUser.ADMIN:
        await task_services.add_task(task_data)
        return JSONResponse(content={"message": "ok"},
                            status_code=status.HTTP_200_OK)


@router.post("/settings", responses={status.HTTP_200_OK: {"message": "ok"}})
async def post_settings_task(task_data: TaskSettings, task_services: TaskServices = Depends(),
                             user: UserGet = Depends(get_current_user)):
    if user.type == TypeUser.ADMIN:
        code = await task_services.add_task_settings(task_data)
        return JSONResponse(content={"message": code},
                            status_code=status.HTTP_200_OK)


@router.put("/", responses={status.HTTP_200_OK: {"message": "ok"}})
async def put_task(task_data: TaskPut, task_services: TaskServices = Depends(),
                   user: UserGet = Depends(get_current_user)):
    if user.type == TypeUser.ADMIN:
        await task_services.update_task(task_data)
        return JSONResponse(content={"message": "ok"},
                            status_code=status.HTTP_200_OK)


@router.put("/settings", responses={status.HTTP_200_OK: {"message": "ok"}})
async def put_settings_task(task_data: TaskSettings, task_services: TaskServices = Depends(),
                            user: UserGet = Depends(get_current_user)):
    if user.type == TypeUser.ADMIN:
        code = await task_services.update_settings_task(task_data)
        return JSONResponse(content={"message": code},
                            status_code=status.HTTP_200_OK)


@router.delete("/{id_task}", response_model=TaskGet)
async def delete_task(id_task: int, task_services: TaskServices = Depends(),
                      user: UserGet = Depends(get_current_user)):
    if user.type == TypeUser.ADMIN:
        task = await task_services.delete_task(id_task)
        return task


@router.get("/get_list_task/{id_contest}", response_model=List[TaskGetView])
async def get_list_task(id_contest: int, task_services: TaskServices = Depends(),
                        user: UserGet = Depends(get_current_user)):
    if user.type == TypeUser.ADMIN:
        return task_services.get_list_task(id_contest)


@router.get("/get_task/{id_task}", response_model=TaskGet)
async def get_task(id_task: int, task_services: TaskServices = Depends(),
                   user: UserGet = Depends(get_current_user)):
    if user.type == TypeUser.ADMIN:
        return task_services.get_task(id_task)


@router.get("/get_settings/{id_task}", response_model=TaskSettings)
async def get_settings(id_task: int, task_services: TaskServices = Depends()):
    settings = await task_services.get_settings(id_task)
    return settings


@router.post("/upload_file/{id_task}", responses={status.HTTP_200_OK: {"message": "ok"}})
async def upload_files(id_task: int,
                       file: UploadFile,
                       task_services: TaskServices = Depends(),
                       user: UserGet = Depends(get_current_user)):
    if user.type == TypeUser.ADMIN:
        code = await task_services.upload_file(id_task, file)
        return JSONResponse(content={"message": code},
                            status_code=status.HTTP_200_OK)


@router.post("/upload_json_files/{id_task}")
async def upload_json_files(id_task: int,
                            file: UploadFile,
                            task_services: TaskServices = Depends(),
                            user: UserGet = Depends(get_current_user)):
    if user.type == TypeUser.ADMIN:
        code = await task_services.upload_json_file(id_task, file)
        return JSONResponse(content={"message": code},
                            status_code=status.HTTP_200_OK)


@router.delete("/delete_file/{id_task}/{filename}", responses={status.HTTP_200_OK: {"message": "ok"}})
async def delete_file(filename: str,
                      id_task: int,
                      task_services: TaskServices = Depends(),
                      user: UserGet = Depends(get_current_user)):
    if user.type == TypeUser.ADMIN:
        code = await task_services.delete_file(id_task, filename)
        return JSONResponse(content={"message": code},
                            status_code=status.HTTP_200_OK)
