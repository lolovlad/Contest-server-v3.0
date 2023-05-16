from fastapi import APIRouter, Depends, Response, status
from typing import List

from ..Models.User import UserGet, UserPost, UserUpdate, UserGetInTeam, TypeUser
from ..Models.Message import StatusUser
from ..Services.LoginServices import get_current_user
from ..Services.UsersServices import UsersServices

router = APIRouter(prefix='/users')


@router.get('/', response_model=List[UserGet])
async def get_users(response: Response, number_page: int = 1, type_user: str | None = None, user_services: UsersServices = Depends()):
    count_page = await user_services.get_count_page()
    response.headers["X-Count-Page"] = str(count_page)
    response.headers["X-Count-Item-User"] = str(user_services.count_item)
    return await user_services.get_list_user(number_page, type_user)


@router.get("/{id_user}", response_model=UserGet)
async def get_user(id_user: int, user_services: UsersServices = Depends()):
    return await user_services.get_user_id(id_user)


@router.get('/status/{id_contest}', response_model=StatusUser)
async def get_status_user(id_contest: int, user_services: UsersServices = Depends(),
                          user: UserGet = Depends(get_current_user)):
    return await user_services.status_user(id_contest, user.id)


@router.post('/')
async def post_user(response: Response,
                    user_services: UsersServices = Depends(),
                    user: UserPost = None,
                    user_data: UserGet = Depends(get_current_user)):
    count_page = await user_services.get_count_page()
    response.headers["X-Count-Page"] = str(count_page)
    response.headers["X-Count-Item-User"] = str(user_services.count_item)
    if user_data.type == TypeUser.ADMIN:
        await user_services.add_user(user)


@router.put('/')
async def put_user(user_data: UserUpdate,
                   user_services: UsersServices = Depends(),
                   user: UserGet = Depends(get_current_user)):
    if user.type == TypeUser.ADMIN:
        await user_services.update_user(user_data.id, user_data)


@router.delete('/{user_id}')
async def delete_user(response: Response,
                      user_id: int,
                      user_services: UsersServices = Depends(),
                      user: UserGet = Depends(get_current_user)):
    count_page = await user_services.get_count_page()
    response.headers["X-Count-Page"] = str(count_page)
    response.headers["X-Count-Item-User"] = str(user_services.count_item)
    if user.type == TypeUser.ADMIN:
        await user_services.delete_user(user_id)


@router.get("/in_team/{id_team}", response_model=List[UserGet])
async def get_in_team_users(id_team: int, user_services: UsersServices = Depends()):
    return await user_services.get_list_in_team_user(id_team)


@router.get("/in_contest/{id_contest}", response_model=dict)
async def get_in_contest_users(id_contest: int, user_services: UsersServices = Depends()):
    return await user_services.get_list_in_contest_user(id_contest)

