import grpc
from grpc.aio import Channel

from fastapi import Depends

from ..Services.protos import answer_pb2, answer_pb2_grpc
from ..grps_review import get_channel

from ..Models.Answer import AnswerGet


from typing import List
from json import loads

class AnswersRepository:
    def __init__(self, channel: Channel = Depends(get_channel)):
        self.__channel: Channel = channel

    async def get_list_answers(self, id_contest: int, id_user: int) -> List[AnswerGet]:
        sub = answer_pb2_grpc.AnswerApiStub(self.__channel)
        response = await sub.GetAnswersContest(answer_pb2.GetAnswersContestRequest(id_contest=id_contest,
                                                                                   id=id_user))

        return [AnswerGet.from_orm(obj) for obj in response.answers]

    def post_answer(self, body_message: dict, id_team: int, id_user: int):
        sub = answer_pb2_grpc.AnswerApiStub(self.__channel)
        request = answer_pb2.SendAnswerRequest(
            id_task=int(body_message["id_task"]),
            id_user=id_user,
            id_team=id_team,
            id_contest=int(body_message["id_contest"]),
            id_compiler=int(body_message["id_compiler"]),
            program_file=body_message["program_file"].encode(),
        )
        return sub.SendAnswer(request)

    async def get_list_answer_by_id_task(self, id_task: int, type_contest: str, id_search: int) -> list:
        sub = answer_pb2_grpc.AnswerApiStub(self.__channel)
        response = await sub.GetListAnswersTask(answer_pb2.GetListAnswersTaskRequest(
            id_task=id_task,
            type_contest=type_contest,
            id=id_search
        ))
        return response.answers

    async def get_report(self, id_answer: int) -> dict:
        sub = answer_pb2_grpc.AnswerApiStub(self.__channel)
        request = answer_pb2.GetReportFileRequest(id_answer=id_answer)
        response = await sub.GetReportFile(request)

        return loads(response.report_file.decode())


    async def get_max_point_answer_by_contest_and_user_id(self, id_contest: int, id_user: int):
        pass