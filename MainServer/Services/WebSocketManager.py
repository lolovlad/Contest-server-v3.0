from fastapi import WebSocket, Depends
from ..Models.WebSocketMessages import User, BaseMessage, TypeMessage, TaskView, GetListTask
from ..Models.Task import TaskGet, TaskSettings
from ..Models.TaskTestSettings import SettingsTest, Test
from ..Models.Contest import TypeContest

from .LoginServices import get_current_user
from .ContestsServices import ContestsServices
from .UsersServices import UsersServices

from sqlalchemy.orm.session import Session

from ..database import get_session
from ..tables import Task, ContestRegistration, Contest
from typing import List

import grpc
from MainServer.Services.protos import settings_pb2_grpc, settings_pb2, jsonTest_pb2_grpc, jsonTest_pb2, \
    compiler_pb2_grpc, compiler_pb2, answer_pb2_grpc, answer_pb2
from ..settings import settings

from json import dumps, loads


class MainViewContestService:
    def __init__(self, session: Session = Depends(get_session),
                 contest_services: ContestsServices = Depends(),
                 user_services: UsersServices = Depends()):
        self.__session: Session = session
        self.__contest_services: ContestsServices = contest_services
        self.__user_services: UsersServices = user_services
        self.__ip_review = f'{settings.server_review_host}:{settings.server_review_port}'

    async def __get_team_user(self, id_user: int, id_contest: int):
        reg = self.__session.query(ContestRegistration).filter(ContestRegistration.id_contest == id_contest)\
            .filter(ContestRegistration.id_user == id_user).first()
        if reg.id_team is not None:
            return reg.id_team
        return 0

    async def get_contest(self, id_contest: int) -> str:
        contest = self.__contest_services.get_contest(id_contest)
        async with grpc.aio.insecure_channel(self.__ip_review) as channel:
            sub = compiler_pb2_grpc.CompilerApiStub(channel)
            response = await sub.GetListCompiler(compiler_pb2.GetListCompilerRequest(count=1))

        contest.users = []
        contest = contest.dict()

        contest["compilers"] = []

        for compiler in response.compilers:
            contest["compilers"].append({
                "name": compiler.name,
                "id": compiler.id,
            })

        print(contest)

        message = BaseMessage(
            message=TypeMessage.GET_CONTEST,
            body_message=contest
        )
        return message.json()

    def get_list_task(self, id_contest: int) -> str:
        tasks = self.__session.query(Task).filter(Task.id_contest == id_contest).all()
        data = GetListTask(list_task=[])
        for task in tasks:
            data.list_task.append(TaskView(id=task.id,
                                           name=task.name_task,
                                           type_task=task.type_task))
        message = BaseMessage(
            message=TypeMessage.GET_LIST_TASK,
            body_message=data.dict()
        )
        return message.json()

    async def get_task(self, id_task: int):
        task_data = self.__session.query(Task).filter(Task.id == id_task).first()
        task = TaskGet(id=id_task,
                       id_contest=task_data.id_contest,
                       name_task=task_data.name_task,
                       description=task_data.description.decode(),
                       description_input=task_data.description_input.decode(),
                       description_output=task_data.description_output.decode(),
                       type_task=task_data.type_task)
        async with grpc.aio.insecure_channel(self.__ip_review) as channel:
            sub = settings_pb2_grpc.SettingsApiStub(channel)
            response_settings = await sub.SettingsGet(settings_pb2.GetSettingsRequest(id=id_task))
            task_settings = TaskSettings(id=id_task,
                                         time_work=response_settings.settings.time_work,
                                         size_raw=response_settings.settings.size_raw,
                                         number_shipments=response_settings.settings.number_shipments,
                                         files=[])
            task_settings.type_input = response_settings.settings.type_input
            task_settings.type_output = response_settings.settings.type_output

            sub = jsonTest_pb2_grpc.JsonTestApiStub(channel)
            response_settings = await sub.GetAllSettingsTests(jsonTest_pb2.GetAllSettingsTestsRequest(id=id_task))
            response_chunk = await sub.GetChunkTest(jsonTest_pb2.GetChunkTestRequest(id=id_task, type_test="test", index=0))

        merge = task.dict()
        task_settings_dict = task_settings.dict()
        for key in task_settings_dict:
            merge[key] = task_settings_dict[key]

        view_settings = []
        for i in response_settings.settings:
            view_settings.append({
                "limitation_variable": i.limitation_variable,
                "necessary_test": i.necessary_test,
                "check_type": i.check_type
            })

        view_test = []
        for i in response_chunk.tests:
            view_test.append({
                "score": i.score,
                "filling_type_variable": i.filling_type_variable,
                "answer": i.answer
            })

        merge["view_settings"] = view_settings
        merge["view_test"] = view_test

        message = BaseMessage(
            message=TypeMessage.GET_SELECT_TASK,
            body_message=merge
        )
        return message.json()

    async def post_answer(self, body_message: dict):
        async with grpc.aio.insecure_channel(self.__ip_review) as channel:
            sub = answer_pb2_grpc.AnswerApiStub(channel)
            user = get_current_user(body_message["token"]["access_token"])
            request = answer_pb2.SendAnswerRequest(
                id_task=body_message["id_task"],
                id_user=user.id,
                id_team=await self.__get_team_user(user.id, body_message["id_contest"]),
                id_contest=body_message["id_contest"],
                id_compiler=body_message["id_compiler"],
                program_file=body_message["program_file"].encode(),
            )
            response = await sub.SendAnswer(request)
        message = BaseMessage(
            message=TypeMessage.POTS_ANSWER,
            body_message={"code": response.code}
        )
        return message.json()

    async def get_list_answers(self, id_task: int, id_contest: int, token: str):
        user = get_current_user(token)

        contest = self.__contest_services.get_contest(id_contest)

        type_contest = "solo" if contest.type == TypeContest.OLIMPIADA else "team"

        id_search = 0
        if type_contest == "team":
            id_search = self.__session.query(ContestRegistration)\
                .filter(ContestRegistration.id_user == user.id)\
                .filter(ContestRegistration.id_contest == id_contest).first().id_team
        else:
            id_search = user.id

        async with grpc.aio.insecure_channel(self.__ip_review) as channel:
            sub = answer_pb2_grpc.AnswerApiStub(channel)
            response = await sub.GetListAnswersTask(answer_pb2.GetListAnswersTaskRequest(
                id_task=id_task,
                type_contest=type_contest,
                id=id_search
            ))
        list_answer = []
        for answer in response.answers:
            user = self.__user_services.get_user_id(answer.id_user)

            task = self.__session.query(Task).filter(Task.id == answer.id_task).first()
            list_answer.append({
                "date_send": answer.date_send,
                "id": answer.id,
                "name_user": f"{user.sename} {user.name[0]}. {user.secondname[0]}.",
                "name_task": task.name_task,
                "name_compilation": answer.name_compilation,
                "total": answer.total,
                "time": answer.time,
                "memory_size": answer.memory_size,
                "number_test": answer.number_test,
                "points": answer.points,
            })
        message = BaseMessage(
            message=TypeMessage.GET_LIST_ANSWER,
            body_message={"list": list_answer}
        )
        return message.json()

    async def get_report(self, id_answer: int):
        async with grpc.aio.insecure_channel(self.__ip_review) as channel:
            sub = answer_pb2_grpc.AnswerApiStub(channel)
            request = answer_pb2.GetReportFileRequest(id_answer=id_answer)
            response = await sub.GetReportFile(request)

        message = BaseMessage(
            message=TypeMessage.GET_REPORT,
            body_message={"report": loads(response.report_file.decode())}
        )
        return message.json()

    async def close_contest(self, id_user: int, id_contest: int):
        contest = self.__session.query(ContestRegistration).filter(ContestRegistration.id_contest == id_contest)\
            .filter(ContestRegistration.id_user == id_user).first()
        contest.state_contest = 2
        self.__session.commit()


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
        if message.message == TypeMessage.GET_CONTEST:
            data = await self.__service.get_contest(message.body_message["id"])
            await self.__send_personal_message(data, websocket)
        if message.message == TypeMessage.GET_LIST_TASK:
            data = self.__service.get_list_task(message.body_message["id"])
            await self.__send_personal_message(data, websocket)
        if message.message == TypeMessage.GET_SELECT_TASK:
            data = await self.__service.get_task(message.body_message["id"])
            await self.__send_personal_message(data, websocket)
        if message.message == TypeMessage.POTS_ANSWER:
            data = await self.__service.post_answer(message.body_message)
            await self.__send_personal_message(data, websocket)
        if message.message == TypeMessage.GET_LIST_ANSWER:
            body = message.body_message
            data = await self.__service.get_list_answers(body["id_task"], body["id_contest"], body["token"]["access_token"])
            await self.__send_personal_message(data, websocket)
        if message.message == TypeMessage.GET_REPORT:
            body = message.body_message
            data = await self.__service.get_report(body["id_answer"])
            await self.__send_personal_message(data, websocket)
        if message.message == TypeMessage.CLOSER_CONTEST:
            body = message.body_message
            user = get_current_user(body["token"]["access_token"])
            await self.__service.close_contest(user.id, body["id_contest"])

    async def __send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_json(message)

    async def __broadcast(self, message: str):
        for connection in self.__active_connections:
            await connection.websocket.send_text(message)