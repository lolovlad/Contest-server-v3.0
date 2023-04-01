from fastapi import WebSocket, Depends
from ..Models.WebSocketMessages import User, BaseMessage, TypeMessage, TaskView, GetListTask
from typing import List
from ..Services.UserContestView import MainViewContestService


class ConnectionManager:
    def __init__(self, service: MainViewContestService = Depends()):
        self.__active_connections: List[User] = []
        self.__token_conaction: dict = {}
        self.__service: MainViewContestService = service

    async def connect(self, websocket: WebSocket, token: str):
        await websocket.accept()
        self.__token_conaction[token] = websocket
        self.__active_connections.append(User(token=token, websocket=websocket))

    def disconnect(self, websocket: WebSocket):
        for connect in self.__active_connections:
            if connect.websocket is websocket:
                self.__token_conaction.pop(connect.token)
                self.__active_connections.remove(connect)
                break

    async def receive(self, message: dict, websocket: WebSocket):
        message = BaseMessage(**message)
        if message.message == TypeMessage.POTS_ANSWER:
            async for data in self.__service.post_answer(message.body_message):
                await self.__send_personal_message(data, websocket)

    async def __send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_json(message)

    async def __broadcast(self, message: str):
        for connection in self.__active_connections:
            await connection.websocket.send_text(message)