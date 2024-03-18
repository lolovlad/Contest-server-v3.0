from fastapi import APIRouter, Depends, UploadFile, Form, File
from fastapi import status
from fastapi.responses import JSONResponse


from ..Services.WebSocketManager import MainViewContestService
from ..Services.LoginServices import get_current_user

from ..Models.ContestView import ContestView
from ..Models.User import UserGet
from ..Models.Task import TaskViewUser, TaskAndTest
from ..Models.Answer import AnswerView, Report


from typing import List

router = APIRouter(prefix="/user_contest_view", tags=["user_contest_view"])


@router.get("/get_contest/{uuid_contest}", response_model=ContestView)
async def get_contest(uuid_contest: str,
                      services: MainViewContestService = Depends()):
    contest = await services.get_contest(uuid_contest)
    return contest


@router.get("/get_list_task/{uuid_contest}", response_model=List[TaskViewUser])
async def get_list_task(uuid_contest: str,
                        user: UserGet = Depends(get_current_user),
                        services: MainViewContestService = Depends()):
    list_task = await services.get_list_task(uuid_contest, user.id)
    return list_task


@router.get("/get_task/{uuid}", response_model=TaskAndTest)
async def get_task(uuid: str, services: MainViewContestService = Depends()):
    task = await services.get_task(uuid)
    return task


@router.get("/get_list_answers/{uuid_contest}/{uuid_task}", response_model=List[AnswerView])
async def get_list_answers(uuid_contest: str,
                           uuid_task: str,
                           services: MainViewContestService = Depends(),
                           user: UserGet = Depends(get_current_user)):
    list_answer = await services.get_list_answers(uuid_task, uuid_contest, user.id)
    return list_answer


@router.get("/get_report/{id_answer}", response_model=Report)
async def get_report(id_answer: int, services: MainViewContestService = Depends()):
    report = await services.get_report(id_answer)
    return report


@router.put("/close_contest/{id_contest}", responses={status.HTTP_200_OK: {"message": "ok"}})
async def close_contest(id_contest: int,
                        user: UserGet = Depends(get_current_user),
                        services: MainViewContestService = Depends()):
    await services.close_contest(user.id, id_contest)
    return JSONResponse(content={"message": "200"},
                        status_code=status.HTTP_200_OK)


@router.post("/send_answer/{uuid_contest}/{uuid_task}", responses={status.HTTP_200_OK: {"message": "ok"}})
async def send_answer(uuid_contest: str,
                      uuid_task: str,
                      user: UserGet = Depends(get_current_user),
                      id_compilation: int = Form(...),
                      file: UploadFile = File(...),
                      services: MainViewContestService = Depends()):
    await services.send_answer(uuid_contest, uuid_task, user.id, id_compilation, file)
    return JSONResponse(content={"message": "200"},
                        status_code=status.HTTP_200_OK)


@router.post("/send_answer_text/{uuid_contest}/{uuid_task}", responses={status.HTTP_200_OK: {"message": "ok"}})
async def send_answer(uuid_contest: str,
                      uuid_task: str,
                      text: str = Form(...),
                      user: UserGet = Depends(get_current_user),
                      services: MainViewContestService = Depends()):
    await services.send_answer_text(uuid_contest, uuid_task, user.id, text)
    return JSONResponse(content={"message": "200"},
                        status_code=status.HTTP_200_OK)