from fastapi import Depends, Form, File

from ..Repositories import CompilationsRepository, \
    AnswersRepository, \
    TaskRepository, UserRepository, ContestsRepository, JsonTestRepository

from ..Models.WebSocketMessages import BaseMessage, TypeMessage
from ..Models.Task import TaskGet, TaskSettings, TaskViewUser, TaskAndTest
from ..Models.Contest import TypeContest
from ..Models.ContestView import ContestView
from ..Models.Answer import AnswerView, Report

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

        id_user = get_current_user(body_message["token"])

        id_team: int = await self.__contest_repository.get_id_team_by_user_and_contest(id_user.id, int(body_message["id_contest"]))

        call = self.__answer_repository.post_answer(body_message, id_team, id_user.id)

        async for info in call:
            message = BaseMessage(
                message=TypeMessage.POTS_ANSWER,
                body_message={"code": info.code}
            )
            yield message.json()
        yield BaseMessage(
            message=TypeMessage.GET_LIST_TASK,
            body_message={"code": "200"}
        ).json()

    async def get_list_answers(self, id_task: int, id_contest: int, id_user: int) -> List[AnswerView]:
        contest = await self.__contest_repository.get_contest(id_contest)

        type_contest = "solo" if contest.type == TypeContest.OLIMPIADA else "team"

        id_search = 0
        if type_contest == "team":
            id_search = await self.__contest_repository.get_id_team_by_user_and_contest(id_user, id_contest)
        else:
            id_search = id_user

        xash_ans = {}

        list_answers_response = await self.__answer_repository.get_list_answer_by_id_task(id_task, type_contest, id_search)

        task = await self.__task_repository.get(id_task)
        list_answer = []

        for answer in list_answers_response:
            if answer.id_user not in xash_ans:
                xash_ans[answer.id_user] = await self.__user_repository.get_user(answer.id_user)
            user = xash_ans[answer.id_user]
            list_answer.append(AnswerView(**{
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
            }))
        return list_answer

    async def get_report(self, id_answer: int) -> Report:
        report = await self.__answer_repository.get_report(id_answer)
        return Report(report=report)

    async def close_contest(self, id_user: int, id_contest: int):
        await self.__contest_repository.update_user_state_contest(id_contest, id_user)

