from ..Models.Contest import ContestGet, ContestPost, ContestDelete, ContestPutUsers, ContestUpdate, ContestCardView, ResultContest
from ..Models.ReportTotal import ReportTotal
#from ..Models.Menu import Menu
from fastapi import Depends, APIRouter, status
from fastapi.responses import JSONResponse
from typing import List

from ..Models.User import UserGet, TypeUser
from ..Services.ContestsServices import ContestsServices
from ..Services.LoginServices import get_current_user

router = APIRouter(prefix="/contests")


@router.get("/list_contest", response_model=List[ContestGet])
def get_list_contest(contest_services: ContestsServices = Depends()):
    return contest_services.get_list_contest()


@router.get("/contests_by_user_id", response_model=List[ContestCardView])
def contests_by_user_id(user: UserGet = Depends(get_current_user),
                        contest_services: ContestsServices = Depends()):
    return contest_services.get_list_contest_by_user_id(user.id)


@router.get("/{id_contest}", response_model=ContestGet)
def get_contest(id_contest: int, contest_services: ContestsServices = Depends()):
    return contest_services.get_contest(id_contest)


@router.post("/")
def post_contest(contest_data: ContestPost, contest_services: ContestsServices = Depends(),
                 user: UserGet = Depends(get_current_user)):
    if user.type == TypeUser.ADMIN:
        contest_services.add_contest(contest_data)


@router.delete("/{id_contest}")
def delete_contest(id_contest: int, contest_services: ContestsServices = Depends(),
                   user: UserGet = Depends(get_current_user)):
    if user.type == TypeUser.ADMIN:
        contest_services.delete_contest(id_contest)


@router.put("/")
def update_contest(contest_data: ContestUpdate, contest_services: ContestsServices = Depends(),
                   user: UserGet = Depends(get_current_user)):
    if user.type == TypeUser.ADMIN:
        contest_services.update_contest(contest_data)


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