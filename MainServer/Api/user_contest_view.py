from fastapi import WebSocket, WebSocketDisconnect, WebSocketException, APIRouter, Depends, Query
from fastapi import status
from fastapi.responses import JSONResponse

from ..Services.WebSocketManager import ConnectionManager
from ..Services.WebSocketManager import MainViewContestService
from ..Services.LoginServices import get_current_user

from ..Models.ContestView import ContestView
from ..Models.User import UserGet
from ..Models.Task import TaskViewUser, TaskAndTest

from asyncio.queues import Queue
from asyncio import gather
import asyncio
from typing import List

router = APIRouter(prefix="/user_contest_view")


@router.get("/get_contest/{id_contest}", response_model=ContestView)
async def get_contest(id_contest: int, services: MainViewContestService = Depends()):
    contest = await services.get_contest(id_contest)
    return contest


@router.get("/get_list_task/{id_contest}", response_model=List[TaskViewUser])
async def get_list_task(id_contest: int, user: UserGet = Depends(get_current_user), services: MainViewContestService = Depends()):
    list_task = await services.get_list_task(id_contest, user.id)
    return list_task


@router.get("/get_task/{id_task}", response_model=TaskAndTest)
async def get_task(id_task: int, services: MainViewContestService = Depends()):
    task = await services.get_task(id_task)
    return task


@router.get("/get_list_answers/{id_contest}/{id_task}", response_model=BaseMessage)
async def get_list_answers(id_contest: int,
                           id_task: int,
                           services: MainViewContestService = Depends(),
                           user: UserGet = Depends(get_current_user)):
    list_answer = await services.get_list_answers(id_task, id_contest, user.id)
    return list_answer


@router.get("/get_report/{id_answer}", response_model=BaseMessage)
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


async def get_token(
    websocket: WebSocket,
    token: str = Query(default=None),
):
    if token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    return token


async def read_from_socket(queue: Queue, websocket: WebSocket):
    async for data in websocket.iter_json():
        queue.put_nowait(data)


async def get_data_and_send(manager: ConnectionManager, websocket: WebSocket, queue: Queue):
    try:
        while True:
            data = await queue.get()
            main_loop = asyncio.get_running_loop()
            main_loop.create_task(manager.receive(data, websocket))
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.websocket("/view_contest")
async def view_contest(websocket: WebSocket, manager: ConnectionManager = Depends(),
                       token: str = Depends(get_token)):
    await manager.connect(websocket, token)
    queue = Queue()
    await gather(read_from_socket(queue, websocket), get_data_and_send(manager, websocket, queue))
    '''try:
        while True:
            data = await websocket.receive_json()
            await manager.receive(data, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)'''