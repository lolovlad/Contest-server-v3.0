from httpx import AsyncClient
from fastapi import Depends

from ..review_service import get_channel
from ..Models.Answer import AnswerGet


from typing import List
from json import loads


class AnswersRepository:
    def __init__(self, client: AsyncClient = Depends(get_channel)):
        self.__client: AsyncClient = client

    async def get_list_answers_by_id_contest(self, id_contest: int, id_user: int) -> List[AnswerGet]:
        response = await self.__client.get(f"answer/list_answer_contest/{id_contest}", params={
            "id_user": id_user
        })

        return [AnswerGet.model_validate(obj) for obj in response.json()]

    async def post_answer(self, body_message: dict, id_user: int, id_team: int = 0):
        request = await self.__client.post(f"answer/send_answer/{body_message['id_task']}", json={
            "id_user": id_user,
            "id_contest": int(body_message["id_contest"]),
            "id_compilation": int(body_message["id_compiler"]),
            "program_file": body_message["program_file"].encode(),
        })

    async def get_list_answer_by_id_task(self, id_task: int, type_contest: str, id_search: int) -> list:
        response = await self.__client.get(f"answer/list_answer_task/{id_task}", params={
            "type_contest": type_contest,
            "id_user": id_search
        })
        return response.json()

    async def get_report(self, id_answer: int) -> dict:
        response = await self.__client.get(f"answer/get_report_file/{id_answer}")
        return loads(response.text)

    async def get_max_point_answer_by_contest_and_user_id(self, id_contest: int, id_user: int):
        pass