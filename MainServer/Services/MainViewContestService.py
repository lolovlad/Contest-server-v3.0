from fastapi import Depends, Form, File, UploadFile

from ..Repositories import CompilationsRepository, \
    AnswersRepository, \
    TaskRepository, UserRepository, ContestsRepository, JsonTestRepository

from ..Models.Task import TaskGet, BaseTaskSettings, TaskViewUser, TaskAndTest, TypeTask
from ..Models.Contest import TypeContest
from ..Models.ContestView import ContestView
from ..Models.Answer import AnswerView, Report, AnswerGet

from .LoginServices import get_current_user

from ..settings import settings

from json import dumps, loads
from typing import List

from io import StringIO


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

    async def get_contest(self, uuid_contest: str) -> ContestView:
        contest = await self.__contest_repository.get_contest_by_uuid(uuid_contest)
        compilations = await self.__compilation_repository.get_list()

        response = ContestView.model_validate(contest, from_attributes=True)
        response.compiler = compilations

        return response

    async def get_list_task(self, uuid_contest: str, id_user: int) -> List[TaskViewUser]:
        contest = await self.__contest_repository.get_contest_by_uuid(uuid_contest)
        answers = await self.__answer_repository.get_list_answers_by_id_contest(contest.id, id_user)

        answers = {entity.id_task: (entity.total, entity.points) for entity in answers}
        tasks = [TaskViewUser.model_validate(obj, from_attributes=True) for obj in contest.tasks]

        for task in tasks:
            if task.id in answers:
                if answers[task.id][0] == "OK" or int(answers[task.id][1]) > 0:
                    task.last_answer = str(answers[task.id][1])
                else:
                    task.last_answer = str(answers[task.id][0])

        return tasks

    async def get_task(self, uuid: str) -> TaskAndTest:
        task_data = await self.__task_repository.get_by_uuid(uuid)
        task = TaskGet(uuid=task_data.uuid,
                       name_task=task_data.name_task,
                       description=task_data.description.decode(),
                       description_input=task_data.description_input.decode(),
                       description_output=task_data.description_output.decode(),
                       type_task=TypeTask.model_validate(task_data.type_task, from_attributes=True),
                       complexity=task_data.complexity,
                       )

        if task_data.type_task.name == "detailed_response":
            merge = task.model_dump()
            task_main = TaskAndTest(**merge)
        else:

            task_settings = await self.__task_repository.get_setting(task_data.id)

            settings_test, chunk_test = await self.__json_test_repo.get_first_test(task_data.id)

            merge = task.model_dump()
            task_settings_dict = task_settings.model_dump()
            for key in task_settings_dict:
                merge[key] = task_settings_dict[key]

            task_main = TaskAndTest(**merge)

            task_main.view_settings = settings_test
            task_main.view_test = chunk_test

        return task_main

    async def send_answer(self,
                          uuid_contest: str,
                          uuid_task: str,
                          user_id: int,
                          id_compilation: int,
                          file: UploadFile):
        task = await self.__task_repository.get_by_uuid(uuid_task)
        contest = await self.__contest_repository.get_contest_by_uuid(uuid_contest)
        await self.__answer_repository.post_answer(
            contest.id,
            task.id,
            task.type_task.name,
            user_id,
            id_compilation,
            file)

    async def get_list_answers(self, uuid_task: str, uuid_contest: str, id_user: int) -> List[AnswerView]:
        contest = await self.__contest_repository.get_contest_by_uuid(uuid_contest)
        task = await self.__task_repository.get_by_uuid(uuid_task)

        xash_ans = {}
        list_answers_response = await self.__answer_repository.get_list_answer_by_id_task(task.id, contest.id, "solo", id_user)
        list_answers_response = [AnswerGet.model_validate(i) for i in list_answers_response]
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
        return Report(report=loads(report["message"]))

    async def close_contest(self, id_user: int, id_contest: int):
        await self.__contest_repository.update_user_state_contest(id_contest, id_user)

    async def send_answer_text(self,
                               uuid_contest: str,
                               uuid_task: str,
                               user_id: int,
                               text: str):

        task = await self.__task_repository.get_by_uuid(uuid_task)
        contest = await self.__contest_repository.get_contest_by_uuid(uuid_contest)

        await self.__answer_repository.post_answer(
            contest.id,
            task.id,
            task.type_task.name,
            user_id,
            0,
            text)
