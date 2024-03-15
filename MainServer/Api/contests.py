from ..Models.Contest import ContestGet, ContestPost, ContestPutUsers, ContestUpdate, \
    ContestCardView, ResultContest, TypeContest, StateContest, ContestToTask, ContestToUserAdd

from fastapi import Depends, APIRouter, status, Response
from fastapi.responses import JSONResponse
from typing import List

from ..Models.User import UserGet, TypeUser
from ..Services.ContestsServices import ContestsServices
from ..Services.LoginServices import get_current_user

router = APIRouter(prefix="/contests", tags=["contest"])


@router.get("/get_type_contest", response_model=list[TypeContest])
async def get_type_contest(contest_services: ContestsServices = Depends()):
    list_type = await contest_services.get_type_contest()
    return list_type


@router.get("/get_state_contest", response_model=list[StateContest])
async def get_state_contest(contest_services: ContestsServices = Depends()):
    list_state = await contest_services.get_state_contest()
    return list_state


@router.get("/list_contest", response_model=List[ContestCardView])
async def get_list_contest(
        response: Response,
        number_page: int = 1,
        contest_services: ContestsServices = Depends()):
    count_page = await contest_services.get_count_page()
    response.headers["X-Count-Page"] = str(count_page)
    response.headers["X-Count-Item"] = str(contest_services.count_item)
    contest_list = await contest_services.get_list_contest(number_page)
    return contest_list


@router.get("/contests_by_user_id", response_model=List[ContestCardView])
def contests_by_user_id(user: UserGet = Depends(get_current_user),
                        contest_services: ContestsServices = Depends()):
    return contest_services.get_list_contest_by_user_id(user.id)


@router.get("/{uuid}", response_model=ContestGet)
async def get_contest(uuid: str, contest_services: ContestsServices = Depends()):
    contest = await contest_services.get_contest(uuid)
    return contest


@router.get("/list_light_contest/", response_model=List[ContestCardView])
async def get_list_light_contest(contest_services: ContestsServices = Depends()):
    return await contest_services.get_light_list()


@router.post("/")
async def post_contest(contest_data: ContestPost, contest_services: ContestsServices = Depends(),
                       user: UserGet = Depends(get_current_user)):
    if user.type.name == "admin":
        await contest_services.add_contest(contest_data)


@router.delete("/{id_contest}")
async def delete_contest(id_contest: str, contest_services: ContestsServices = Depends(),
                         user: UserGet = Depends(get_current_user)):
    if user.type.name == "admin":
        await contest_services.delete_contest(id_contest)


@router.put("/{uuid}")
async def update_contest(uuid: str,
                         contest_data: ContestUpdate,
                         contest_services: ContestsServices = Depends(),
                         user: UserGet = Depends(get_current_user)):
    if user.type.name == "admin":
        await contest_services.update_contest(uuid, contest_data)


@router.put("/registration_users")
def registration_users_contest(contest_data: ContestPutUsers, contest_services: ContestsServices = Depends(),
                               user: UserGet = Depends(get_current_user)):
    if user.type == TypeUser.ADMIN:
        contest_services.add_users_contest(contest_data)


@router.get("/report_total/{id_contest}", response_model=ResultContest)
async def get_report_total(id_contest: int, contest_services: ContestsServices = Depends()):
    return await contest_services.get_report_total(id_contest)


@router.put("/update_state_user_in_contest/{id_contest}", responses={status.HTTP_200_OK: {"message": "ok"}})
async def update_state_user_in_contest(id_contest: int,
                                       contest_services: ContestsServices = Depends(),
                                       user: UserGet = Depends(get_current_user)):
    await contest_services.update_state_user_contest(id_contest, user.id)
    return JSONResponse(content={"message": "ok"},
                        status_code=status.HTTP_200_OK)


@router.post("/registration_task")
async def registration_task_to_contest(
        contest_data: ContestToTask,
        contest_services: ContestsServices = Depends(),
        user: UserGet = Depends(get_current_user)):
    if user.type.name == "admin":
        await contest_services.registrate_task_in_contest(contest_data.uuid_task,
                                                          contest_data.uuid_contest)


@router.delete("/registration_task/{uuid_task}/{uuid_contest}")
async def delete_registration_task_to_contest(
        uuid_task: str,
        uuid_contest: str,
        contest_services: ContestsServices = Depends(),
        user: UserGet = Depends(get_current_user)):
    if user.type.name == "admin":
        await contest_services.delete_task_in_contest(uuid_task,
                                                      uuid_contest)


@router.post("/registration_user")
async def registration_task_to_contest(
        contest_data: ContestToUserAdd,
        contest_services: ContestsServices = Depends(),
        user: UserGet = Depends(get_current_user)):
    if user.type.name == "admin":
        await contest_services.registrate_user_in_contest(contest_data.id_user,
                                                          contest_data.uuid_contest)


@router.delete("/registration_user/{id_user}/{uuid_contest}")
async def delete_registration_task_to_contest(
        id_user: int,
        uuid_contest: str,
        contest_services: ContestsServices = Depends(),
        user: UserGet = Depends(get_current_user)):
    if user.type.name == "admin":
        await contest_services.delete_user_in_contest(id_user,
                                                      uuid_contest)
