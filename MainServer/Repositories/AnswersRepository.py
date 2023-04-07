import grpc
from grpc.aio import Channel

from fastapi import Depends

from ..Services.protos import answer_pb2, answer_pb2_grpc
from ..grps_review import get_channel

from ..Models.Answer import AnswerGet

from typing import List


class AnswersRepository:
    def __init__(self, channel: Channel = Depends(get_channel)):
        self.__channel: Channel = channel

    async def get_list_answers(self, id_contest: int, id_user: int) -> List[AnswerGet]:
        sub = answer_pb2_grpc.AnswerApiStub(self.__channel)
        response = await sub.GetAnswersContest(answer_pb2.GetAnswersContestRequest(id_contest=id_contest,
                                                                                   id=id_user))

        return [AnswerGet.from_orm(obj) for obj in response.answers]