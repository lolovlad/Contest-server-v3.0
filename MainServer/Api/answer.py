from fastapi import Depends, Response, APIRouter
from ..Services.AnswerService import AnswerService
from ..Models.Answer import AnswerGet, GetAnswerNew, AnswerReview, PutPointAnswer
from ..Models.User import UserGet

from ..Services.LoginServices import get_current_user


router = APIRouter(prefix="/answers", tags=["answer"])


@router.get("/{uuid_contest}/{uuid_task}/{id_user}/list", response_model=list[GetAnswerNew])
async def get_list_contest(
        uuid_contest: str,
        uuid_task: str,
        id_user: int,
        response: Response,
        number_page: int = 1,
        answer_service: AnswerService = Depends()):
    count_page, count_item, list_ans = await answer_service.get_list_answers(
        uuid_contest,
        uuid_task,
        id_user,
        number_page
    )
    response.headers["X-Count-Page"] = str(count_page)
    response.headers["X-Count-Item"] = str(count_item)
    return list_ans


@router.get("/review/{id_answer}", response_model=AnswerReview)
async def get_review_answer(id_answer: int,
                            user: UserGet = Depends(get_current_user),
                            answer_service: AnswerService = Depends()):
    if user.type.name == "admin":
        entity = await answer_service.get_review_answer(id_answer)
        return entity


@router.put("/review/point/{id_answer}")
async def update_point_answer(id_answer: int,
                              answer: PutPointAnswer,
                              user: UserGet = Depends(get_current_user),
                              answer_service: AnswerService = Depends()):
    if user.type.name == "admin":
        await answer_service.update_point_answer(id_answer, answer)