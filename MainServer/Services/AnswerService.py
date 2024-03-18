from fastapi import Depends

from ..Models.Answer import AnswerGet, AnswerReview, PutPointAnswer
from ..Repositories.AnswersRepository import AnswersRepository
from ..Repositories.ContestRepository import ContestsRepository
from ..Repositories.TaskRepository import TaskRepository


class AnswerService:
    def __init__(self,
                 repo: AnswersRepository = Depends(),
                 repo_contest: ContestsRepository = Depends(),
                 repo_task: TaskRepository = Depends()):
        self.__repo: AnswersRepository = repo
        self.__repo_contest: ContestsRepository = repo_contest
        self.__repo_task: TaskRepository = repo_task

    async def get_list_answers(self,
                               uuid_contest: str,
                               uuid_task: str,
                               id_user: int,
                               page: int = 1) -> (int, int, list[AnswerGet]):
        contest = await self.__repo_contest.get_contest_by_uuid(uuid_contest)
        task = await self.__repo_task.get_by_uuid(uuid_task)

        response = await self.__repo.get_list_answer(contest.id,
                                                     task.id,
                                                     id_user,
                                                     page)
        return response

    async def get_review_answer(self, id_answer: int) -> AnswerReview:
        answer = await self.__repo.get_review_answer(id_answer)
        return answer

    async def update_point_answer(self, id_answer: int, answer_data: PutPointAnswer):
        await self.__repo.update_point_answer(id_answer, answer_data)