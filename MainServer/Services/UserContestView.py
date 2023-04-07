from fastapi import Depends, Form, File

from ..Repositories import CompilationsRepository, \
    AnswersRepository, \
    TaskRepository, UserRepository, ContestsRepository, JsonTestRepository

from ..Models.WebSocketMessages import BaseMessage, TypeMessage
from ..Models.Task import TaskGet, TaskSettings, TaskViewUser, TaskAndTest
from ..Models.Contest import TypeContest
from ..Models.ContestView import ContestView

from .LoginServices import get_current_user

from ..settings import settings

from json import dumps, loads
from typing import List


class MainViewContestService:
    def __init__(self,
                 contest_repository: ContestsRepository = Depends(),
                 user_repository: UserRepository = Depends(),
                 compilation_repository: CompilationsRepository = Depends(),
                 answer_repository: AnswersRepository = Depends(),
                 task_repository: TaskRepository = Depends(),
                 json_test_repo: JsonTestRepository = Depends()):
        self.__contest_repository: ContestsRepository = contest_repository
        self.__user_repository: UserRepository = user_repository
        self.__compilation_repository: CompilationsRepository = compilation_repository
        self.__answer_repository: AnswersRepository = answer_repository
        self.__task_repository: TaskRepository = task_repository
        self.__json_test_repo: JsonTestRepository = json_test_repo

    async def get_contest(self, id_contest: int) -> ContestView:
        contest = await self.__contest_repository.get_contest(id_contest)
        compilations = await self.__compilation_repository.get_list()

        response = ContestView.from_orm(contest)
        response.compiler = compilations

        return response

    async def get_list_task(self, id_contest: int, id_user: int) -> List[TaskViewUser]:
        answers = await self.__answer_repository.get_list_answers(id_contest, id_user)
        answers = {entity.id_task: (entity.total, entity.points) for entity in answers}
        tasks = await self.__task_repository.get_list_task_view_by_id_contest(id_contest)

        for task in tasks:
            if task.id in answers:
                if answers[task.id][0] == "OK" or int(answers[task.id][1]) > 0:
                    task.last_answer = str(answers[task.id][1])
                else:
                    task.last_answer = str(answers[task.id][0])

        return tasks

    async def get_task(self, id_task: int) -> TaskAndTest:
        task_data = await self.__task_repository.get(id_task)
        task = TaskGet(id=id_task,
                       id_contest=task_data.id_contest,
                       name_task=task_data.name_task,
                       description=task_data.description.decode(),
                       description_input=task_data.description_input.decode(),
                       description_output=task_data.description_output.decode(),
                       type_task=task_data.type_task)

        task_settings = await self.__task_repository.get_setting(id_task)

        settings_test, chunk_test = await self.__json_test_repo.get_first_test(id_task)

        merge = task.dict()
        task_settings_dict = task_settings.dict()
        for key in task_settings_dict:
            merge[key] = task_settings_dict[key]

        task_main = TaskAndTest(**merge)

        task_main.view_settings = settings_test
        task_main.view_test = chunk_test

        return task_main

    async def post_answer(self, body_message: dict):
        async with grpc.aio.insecure_channel(self.__ip_review) as channel:
            sub = answer_pb2_grpc.AnswerApiStub(channel)
            user = get_current_user(body_message["token"])
            request = answer_pb2.SendAnswerRequest(
                id_task=int(body_message["id_task"]),
                id_user=user.id,
                id_team=await self.__get_team_user(user.id, body_message["id_contest"]),
                id_contest=int(body_message["id_contest"]),
                id_compiler=int(body_message["id_compiler"]),
                program_file=body_message["program_file"].encode(),
            )
            call = sub.SendAnswer(request)
            async for info in call:
                print("request_answer", info)
                message = BaseMessage(
                    message=TypeMessage.POTS_ANSWER,
                    body_message={"code": info.code}
                )
                yield message.json()
            yield BaseMessage(
                message=TypeMessage.GET_LIST_TASK,
                body_message={"code": info.code}
            ).json()

    async def get_list_answers(self, id_task: int, id_contest: int, id_user: int) -> BaseMessage:
        contest = self.__contest_services.get_contest(id_contest)

        type_contest = "solo" if contest.type == TypeContest.OLIMPIADA else "team"

        id_search = 0
        if type_contest == "team":
            id_search = self.__session.query(ContestRegistration)\
                .filter(ContestRegistration.id_user == id_user)\
                .filter(ContestRegistration.id_contest == id_contest).first().id_team
        else:
            id_search = id_user

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
            return message

    async def get_report(self, id_answer: int):
        async with grpc.aio.insecure_channel(self.__ip_review) as channel:
            sub = answer_pb2_grpc.AnswerApiStub(channel)
            request = answer_pb2.GetReportFileRequest(id_answer=id_answer)
            response = await sub.GetReportFile(request)

        message = BaseMessage(
            message=TypeMessage.GET_REPORT,
            body_message={"report": loads(response.report_file.decode())}
        )
        return message

    async def close_contest(self, id_user: int, id_contest: int):
        contest = self.__session.query(ContestRegistration).filter(ContestRegistration.id_contest == id_contest)\
            .filter(ContestRegistration.id_user == id_user).first()
        contest.state_contest = 2
        self.__session.commit()
