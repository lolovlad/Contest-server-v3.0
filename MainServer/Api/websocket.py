from fastapi import Depends, Response, APIRouter, WebSocket, WebSocketDisconnect, WebSocketException, Query
from fastapi import status

from asyncio.queues import Queue
from asyncio import gather
import asyncio
from ..Services.WebSocketManager import ConnectionManager
from ..Services.MainViewContestService import MainViewContestService
from ..Models.Answer import AnswerGet, GetAnswerNew, AnswerReview, PutPointAnswer
from ..Models.User import UserGet

from ..Services.LoginServices import get_current_user


router = APIRouter(prefix="/websocket", tags=["websocket"])

manager = ConnectionManager()


async def get_user(
    websocket: WebSocket,
    token: str = Query(default=None),
) -> UserGet | None:
    if token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    try:
        if token == "microservice":
            return None
        else:
            user = get_current_user(token)
            return user
    except Exception:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)


async def read_from_socket(queue: Queue, websocket: WebSocket):
    async for data in websocket.iter_json():
        queue.put_nowait(data)


async def get_data_and_send(websocket: WebSocket, service: MainViewContestService, queue: Queue, user: UserGet):
    try:
        while True:
            data = await queue.get()
            main_loop = asyncio.get_running_loop()
            main_loop.create_task(manager.receive(data, service, user))
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.websocket("/view_contest")
async def view_contest(websocket: WebSocket,
                       service: MainViewContestService = Depends(),
                       user: UserGet | None = Depends(get_user)):
    await manager.connect(websocket, user)
    queue = Queue()
    await gather(read_from_socket(queue, websocket), get_data_and_send(websocket, service, queue, user))
    try:
        while True:
            data = await websocket.receive_json()
            await manager.receive(data, service, user)
    except WebSocketDisconnect:
        manager.disconnect(websocket, user)