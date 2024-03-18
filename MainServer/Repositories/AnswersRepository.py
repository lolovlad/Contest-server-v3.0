from httpx import AsyncClient
from fastapi import Depends, UploadFile

from ..review_service import get_channel
from ..Models.Answer import AnswerGet, AnswerView, GetAnswerNew, AnswerReview, PutPointAnswer


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

    async def post_answer(self,
                          id_contest: int,
                          id_task: int,
                          type_task: str,
                          id_user: int,
                          id_compilation: int,
                          file: UploadFile | str):
        if type_task == "programming":
            file_new = {'file': (file.filename, file.file)}
        else:
            file_new = {'file': ("answer.txt", file.encode())}
        request = await self.__client.post(f"answer/send_answer/{id_task}",
                                           data={
                                               "id_compilation": id_compilation,
                                               "id_user": id_user,
                                               "type_task": type_task,
                                               "id_contest": id_contest
                                           },
                                           files=file_new)

    async def get_list_answer_by_id_task(self, id_task: int, id_contest: int, type_contest: str, id_user: int) -> list:
        response = await self.__client.get(f"answer/list_answer_task/{id_contest}/{id_task}", params={
            "type_contest": type_contest,
            "id_user": id_user
        })
        return response.json()

    async def get_report(self, id_answer: int) -> dict:
        response = await self.__client.get(f"answer/get_report_file/{id_answer}")
        return loads(response.text)

    async def get_max_point_answer_by_contest_and_user_id(self, id_contest: int, id_user: int):
        pass

    async def get_list_answer(self,
                              id_contest: int,
                              id_task: int,
                              id_user: int,
                              page: int = 1) -> (int, int, list[GetAnswerNew]):
        try:
            response = await self.__client.get(f"answer/{id_contest}/{id_task}/{id_user}/list", params={"page": page})
            list_ans = [GetAnswerNew.model_validate(i) for i in response.json()]
            return response.headers["X-Count-Page"], response.headers["X-Count-Item"], list_ans
        except:
            return 0, 0, None

    async def get_review_answer(self, id_answer: int) -> AnswerReview:
        try:
            response = await self.__client.get(f"answer/review/{id_answer}")
            return AnswerReview.model_validate(response.json())
        except:
            return None

    async def update_point_answer(self, id_answer: int, answer_data: PutPointAnswer):
        try:
            await self.__client.put(f"answer/review/point/{id_answer}", json=answer_data.model_dump())
        except:
            return None


