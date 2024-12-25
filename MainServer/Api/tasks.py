from fastapi import APIRouter, Depends, File, UploadFile, status, UploadFile, Response

from fastapi.responses import JSONResponse

from ..Models.User import UserGet, TypeUser
from ..Services.LoginServices import get_current_user
from ..Services.TaskServices import TaskServices
from ..Services.FileServices import FileServices
from ..Models.Task import TaskGet, BaseTaskSettings, TaskPut, TaskPost, TaskGetView, GetTaskSettings, TypeTask, TaskToContest

from typing import List


router = APIRouter(prefix="/tasks", tags=["task"])


@router.get("/type_task/", response_model=list[TypeTask])
async def get_type_task(task_services: TaskServices = Depends()):
    type_task_list = await task_services.get_type_task()
    return type_task_list


@router.post("/", responses={status.HTTP_200_OK: {"message": "ok"}})
async def post_task(task_data: TaskPost, task_services: TaskServices = Depends(),
                    user: UserGet = Depends(get_current_user)):
    if user.type.name == "admin":
        await task_services.add_task(task_data)
        return JSONResponse(content={"message": "ok"},
                            status_code=status.HTTP_200_OK)


@router.post("/settings", responses={status.HTTP_200_OK: {"message": "ok"}})
async def post_settings_task(task_data: BaseTaskSettings, task_services: TaskServices = Depends(),
                             user: UserGet = Depends(get_current_user)):
    if user.type == TypeUser.ADMIN:
        code = await task_services.add_task_settings(task_data)
        return JSONResponse(content={"message": code},
                            status_code=status.HTTP_200_OK)


@router.put("/{uuid}", responses={status.HTTP_200_OK: {"message": "ok"}})
async def put_task(uuid: str,
                   task_data: TaskPut,
                   task_services: TaskServices = Depends(),
                   user: UserGet = Depends(get_current_user)):
    if user.type.name == "admin":
        await task_services.update_task(uuid, task_data)
        return JSONResponse(content={"message": "ok"},
                            status_code=status.HTTP_200_OK)


@router.put("/settings/{uuid}", responses={status.HTTP_200_OK: {"message": "ok"}})
async def put_settings_task(uuid: str,
                            task_data: BaseTaskSettings,
                            task_services: TaskServices = Depends(),
                            user: UserGet = Depends(get_current_user)):
    if user.type.name == "admin":
        code = await task_services.update_settings_task(uuid, task_data)
        return JSONResponse(content={"message": "Reset"},
                            status_code=status.HTTP_200_OK)


@router.delete("/{uuid}")
async def delete_task(uuid: str,
                      task_services: TaskServices = Depends(),
                      user: UserGet = Depends(get_current_user)):
    if user.type.name == "admin":
        await task_services.delete_task(uuid)


@router.get("/get_list_task/", response_model=List[TaskGetView])
async def get_list_task(response: Response,
                        num_page: int = 1,
                        task_services: TaskServices = Depends(),
                        user: UserGet = Depends(get_current_user)):
    if user.type.name == "admin":
        count_page = await task_services.get_count_page()
        response.headers["X-Count-Page"] = str(count_page)
        response.headers["X-Count-Item"] = str(task_services.count_item)
        return await task_services.get_list_task(num_page)


@router.get("/get_task/{uuid}", response_model=TaskGet)
async def get_task(uuid: str,
                   task_services: TaskServices = Depends(),
                   user: UserGet = Depends(get_current_user)):
    if user.type.name == "admin":
        return await task_services.get_task(uuid)


@router.get("/get_settings/{uuid}", response_model=GetTaskSettings)
async def get_settings(uuid: str,
                       task_services: TaskServices = Depends()):
    settings = await task_services.get_settings(uuid)
    return settings


@router.post("/upload_file/{uuid}", responses={status.HTTP_200_OK: {"message": "ok"}})
async def upload_files(uuid: str,
                       file: UploadFile,
                       task_services: TaskServices = Depends(),
                       user: UserGet = Depends(get_current_user)):
    if user.type.name == "admin":
        await task_services.upload_file(uuid, file)
        return JSONResponse(content={"message": "Ok"},
                            status_code=status.HTTP_200_OK)


@router.post("/upload_json_files/{uuid}")
async def upload_json_files(uuid: str,
                            file: UploadFile,
                            task_services: TaskServices = Depends(),
                            user: UserGet = Depends(get_current_user)):
    if user.type.name == "admin":
        code = await task_services.upload_json_file(uuid, file)
        return JSONResponse(content={"message": "Ok"},
                            status_code=status.HTTP_200_OK)


@router.delete("/delete_file/{uuid}/{filename}", responses={status.HTTP_200_OK: {"message": "ok"}})
async def delete_file(filename: str,
                      uuid: str,
                      task_services: TaskServices = Depends(),
                      user: UserGet = Depends(get_current_user)):
    if user.type.name == "admin":
        code = await task_services.delete_file(uuid, filename)
        return JSONResponse(content={"message": "ok"},
                            status_code=status.HTTP_200_OK)


@router.get("/task_flag_contest/{uuid_contest}", response_model=list[TaskToContest])
async def task_flag_contest(uuid_contest: str,
                            task_services: TaskServices = Depends()):
    return await task_services.get_list_task_flag_contest(uuid_contest)


@router.get('/get/search', response_model=List[TaskGetView])
async def get_task_search(search_field: str,
                          count: int = 5,
                          task_services: TaskServices = Depends()):
    list_task = await task_services.get_task_by_search_filed(search_field, count)
    return list_task