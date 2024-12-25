import uuid

from fastapi import WebSocket, Depends
from ..Models.WebSocketMessages import User, BaseMessage, TypeMessage, TypePool
from typing import List
from ..Services.MainViewContestService import MainViewContestService
from ..Models.User import UserGet

from json import dumps


class ConnectionManager:
    def __init__(self):
        self.__user_pool: dict[int | str, User] = {}

        self.__pools_chanel: dict = {name_pool: {} for name_pool in TypePool}

    async def connect(self, websocket: WebSocket, user: UserGet | None):
        await websocket.accept()
        if user is not None:
            self.__user_pool[user.id] = User(user=user, websocket=websocket)
        else:
            self.__user_pool[str(uuid.uuid4())] = User(user=None, websocket=websocket)

    def disconnect(self, websocket: WebSocket, user: UserGet | None = 0):
        if user is not None:
            user_id = user.id
            user_socket: User = self.__user_pool[user_id]
            if user_socket.websocket is websocket:
                del self.__user_pool[user_id]
        else:
            for key, user in self.__user_pool.items():
                if user.websocket is websocket:
                    del self.__user_pool[key]

    async def receive(self, message: dict, service: MainViewContestService, user: UserGet | None):
        message = BaseMessage(**message)
        if message.type_message == TypeMessage.SUBSCRIBE_ANSWER:

            id_task = message.body_message["id_task"]
            id_contest = message.body_message["id_contest"]

            pool: dict = self.__pools_chanel[TypePool.ANSWER]

            if pool.get(id_contest) is None:
                self.__pools_chanel[TypePool.ANSWER][id_contest] = {
                    id_task: [user.id]
                }
            else:
                if self.__pools_chanel[TypePool.ANSWER][id_contest].get(id_task) is None:
                    self.__pools_chanel[TypePool.ANSWER][id_contest][id_task] = [user.id]
                else:
                    self.__pools_chanel[TypePool.ANSWER][id_contest][id_task].append(user.id)

        if message.type_message == TypeMessage.SUBSCRIBE_TABLE:

            id_contest = message.body_message["id_contest"]

            pool: dict = self.__pools_chanel[TypePool.TABLE]

            if pool.get(id_contest) is None:
                self.__pools_chanel[TypePool.TABLE][id_contest] = [user.id]
            else:
                self.__pools_chanel[TypePool.TABLE][id_contest].append(user.id)

        if message.type_message == TypeMessage.ANSWER_UPDATE:
            id_task = message.body_message["id_task"]
            id_contest = message.body_message["id_contest"]
            id_user_message = message.body_message["id_user"]

            id_contest, id_task = await service.get_contest_and_task_uuid(id_contest, id_task)

            id_sub_users = self.__pools_chanel[TypePool.ANSWER][id_contest][id_task]

            for id_user in id_sub_users:
                if id_user == id_user_message:
                    await self.__send_personal_message({
                        "type_message": "update_answer",
                        "id_contest": id_contest,
                        "id_task": id_task
                    }, self.__user_pool[id_user].websocket)
                    break

        if message.type_message == TypeMessage.UNSUBSCRIBE_ANSWER:

            id_task = message.body_message["id_task"]
            id_contest = message.body_message["id_contest"]

            pool: dict = self.__pools_chanel[TypePool.ANSWER]

            if pool.get(id_contest) is None:
                return
            else:
                users = self.__pools_chanel[TypePool.ANSWER][id_contest][id_task]
                for i in range(len(users)):
                    if users[i] == user.id:
                        self.__pools_chanel[TypePool.ANSWER][id_contest][id_task].pop(i)
                        break
            if len(self.__pools_chanel[TypePool.ANSWER][id_contest][id_task]) == 0:
                del self.__pools_chanel[TypePool.ANSWER][id_contest][id_task]
            if len(self.__pools_chanel[TypePool.ANSWER][id_contest]) == 0:
                del self.__pools_chanel[TypePool.ANSWER][id_contest]

        if message.type_message == TypeMessage.UNSUBSCRIBE_TABLE:

            id_contest = message.body_message["id_contest"]

            pool: dict = self.__pools_chanel[TypePool.TABLE]

            if pool.get(id_contest) is None:
                return
            else:
                users = self.__pools_chanel[TypePool.TABLE][id_contest]
                for i in range(users):
                    if users[i] == user.id:
                        self.__pools_chanel[TypePool.TABLE][id_contest].pop(i)
                        break
            if len(self.__pools_chanel[TypePool.TABLE][id_contest]) == 0:
                del self.__pools_chanel[TypePool.TABLE][id_contest]
        print("message", message.type_message, "user", user)

    async def __send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    #async def __broadcast(self, message: str):
    #    for connection in self.__active_connections:
    #        await connection.websocket.send_text(message)