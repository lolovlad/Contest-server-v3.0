from fastapi import Depends
from ..Models.Contest import ContestGet, ContestPost, UserContest, \
    ContestPutUsers, ContestUpdate, ContestCardView, TypeContest, \
    ResultContest, TotalContest, StateContest, ContestUserMenu, ContestUserAndTask
from ..Models.User import StateUser

from typing import List
from ..tables import Contest
from ..settings import settings

from datetime import timedelta, datetime
from uuid import uuid4

from ..Repositories import ContestsRepository, UserRepository, TaskRepository


class ContestsServices:
    def __init__(self,
                 contest_repo: ContestsRepository = Depends(),
                 user_repo: UserRepository = Depends(),
                 task_repo: TaskRepository = Depends()):
        self.__time_zone = timedelta(hours=4)
        self.__ip_review = f'{settings.server_review_host}:{settings.server_review_port}'
        self.__repo: ContestsRepository = contest_repo
        self.__user_repo: UserRepository = user_repo
        self.__task_repo: TaskRepository = task_repo
        self.__count_item: int = 20

    @property
    def count_item(self) -> int:
        return self.__count_item

    async def get_count_page(self) -> int:
        count_row = await self.__repo.count_row()
        i = int(count_row % self.__count_item != 0)
        return count_row // self.__count_item + i

    def __convert_contest(self, contest: Contest) -> ContestGet:
        if len(contest.users) != 0:
            users = list(map(lambda x: UserContest(id=x.user.id,
                                                   name=x.user.name,
                                                   sename=x.user.sename,
                                                   secondname=x.user.secondname), contest.users))
        else:
            users = []
        contest_reg = ContestGet(id=contest.id,
                                 users=users,
                                 name_contest=contest.name_contest,
                                 datetime_start=contest.datetime_start,
                                 datetime_end=contest.datetime_end,
                                 datetime_registration=contest.datetime_registration,
                                 description=contest.description,
                                 type=contest.type,
                                 state_contest=contest.state_contest,
                                 tasks=[])
        return contest_reg

    async def get_list_contest(self, number_page: int) -> list[ContestCardView]:
        offset = (number_page - 1) * self.__count_item
        contests_list_entity = await self.__repo.get_list_contest(offset, self.__count_item)
        contest_reg = [ContestCardView.model_validate(i, from_attributes=True) for i in contests_list_entity]
        return contest_reg

    async def get_contest(self, uuid: str) -> ContestGet:
        contest = await self.__repo.get_contest_by_uuid(uuid)
        return ContestGet.model_validate(contest, from_attributes=True)

    async def add_contest(self, contest_data: ContestPost):
        contest = Contest(
            uuid=uuid4(),
            name_contest=contest_data.name_contest,
            datetime_start=datetime.strptime(contest_data.datetime_start, '%Y-%m-%dT%H:%M:%S.%fZ'),
            datetime_end=datetime.strptime(contest_data.datetime_end, '%Y-%m-%dT%H:%M:%S.%fZ'),
            id_type=contest_data.id_type,
            id_state_contest=contest_data.id_state_contest,
            description=contest_data.description.encode())

        await self.__repo.add(contest)

    async def delete_contest(self, id_contest: str):
        contest = await self.__repo.get_contest_by_uuid(id_contest)
        #ts_service = TaskServices()
        #if contest.tasks is not None:
        #    for task in contest.tasks:
        #        await ts_service.delete_task(task.id)
        await self.__repo.delete(contest)

    async def update_contest(self, uuid, contest_data: ContestUpdate):
        contest = await self.__repo.get_contest_by_uuid(uuid)
        for field, val in contest_data:
            if field in ("name_contest", "state_contest"):
                setattr(contest, field, val)
            elif field in ("datetime_start", "datetime_end"):
                try:
                    setattr(contest, field, datetime.strptime(val, '%Y-%m-%dT%H:%M:%S.%fZ'))
                except:
                    setattr(contest, field, datetime.strptime(val, '%Y-%m-%dT%H:%M:%S'))
            if field == "description":
                setattr(contest, field, val.encode())
        await self.__repo.update(contest)

    async def add_users_contest(self, contest_data: ContestPutUsers):
        await self.__repo.add_users_contest(contest_data)

    async def get_light_list(self) -> List[ContestCardView]:
        contest_list = await self.__repo.get_admin_panel_view_contest()
        card_view = []
        for entity in contest_list:
            card_view.append(ContestCardView(
                id=entity[0],
                name_contest=entity[2],
                type=entity[3],
                state_contest=entity[1],
                is_view=True
            ))
        return card_view

    async def get_list_contest_by_user_id(self, id_user: int) -> list[ContestUserMenu]:
        contests_reg = await self.__repo.get_contest_registration(id_user)
        card_view = []

        for contest_registration in contests_reg:
            is_view = True

            if contest_registration.state_contest == StateUser.BANNED:
                is_view = False

            contest = await self.__repo.get_contest(contest_registration.id_contest)

            if contest.state_contest.name != "passes":
                is_view = False

            contest_model = ContestCardView.model_validate(contest, from_attributes=True)
            card_view.append(ContestUserMenu(
                contest=contest_model,
                is_view=is_view
            ))
        return card_view

    async def get_report_total(self, uuid_contest: str) -> ResultContest:
        contest = await self.__repo.get_contest_by_uuid(uuid_contest)

        set_id = await self.__repo.set_id_users(contest.id)

        reports = ResultContest()
        table_result = await self.__repo.get_list_report_total(contest.id)

        reports.name_contest = contest.name_contest
        reports.type_contest = contest.type
        reports.count_user = len(set_id)
        reports.count_task = len(contest.tasks)

        rows = []

        for id_user in table_result:
            table_result[id_user]["sum_point"] = sum(i["points"] for i in table_result[id_user]['task'].values())
            rows.append(table_result[id_user])
        reports.rows = list(sorted(rows, key=lambda i: i["sum_point"], reverse=True))
        return reports

    async def update_state_user_contest(self, uuid_contest: str, id_user: int):
        contest = await self.__repo.get_contest_by_uuid(uuid_contest)
        await self.__repo.update_user_state_contest(contest.id, id_user)

    async def get_type_contest(self) -> list[TypeContest]:
        entity = await self.__repo.get_type_contest()
        return [TypeContest.model_validate(i, from_attributes=True) for i in entity]

    async def get_state_contest(self) -> list[StateContest]:
        entity = await self.__repo.get_state_contest()
        return [StateContest.model_validate(i, from_attributes=True) for i in entity]

    async def registrate_task_in_contest(self, uuid_task: str, uuid_contest: str):
        contest = await self.__repo.get_contest_by_uuid(uuid_contest)
        task = await self.__task_repo.get_by_uuid(uuid_task)
        await self.__repo.add_task_to_contest(task.id, contest.id)
        table = contest.table_result
        if len(table) != 0:
            for id_user in table:
                table[str(id_user)]["task"][str(task.id)] = {
                    "name": task.name_task,
                    "total": "-",
                    "points": 0
                }
        await self.__repo.update_contest_table_result(contest, table)

    async def delete_task_in_contest(self, uuid_task: str, uuid_contest: str):
        contest = await self.__repo.get_contest_by_uuid(uuid_contest)
        task = await self.__task_repo.get_by_uuid(uuid_task)
        await self.__repo.delete_task_in_contest(task.id, contest.id)

        table = contest.table_result
        if len(table) != 0:
            for id_user in table:
                del table[str(id_user)]["task"][str(task.id)]

        await self.__repo.update_contest_table_result(contest, table)

    async def registrate_user_in_contest(self, id_user: int, uuid_contest: str):
        contest = await self.__repo.get_contest_by_uuid(uuid_contest)
        user = await self.__user_repo.get_user(id_user)
        await self.__repo.add_user_to_contest(id_user, contest.id)
        task = {}
        table = contest.table_result
        for task_model in contest.tasks:
            task[int(task_model.id)] = {
                "name": task_model.name_task,
                "total": "-",
                "points": 0
            }

        table[int(id_user)] = {
            "FIO": f"{user.sename} {user.name} {user.secondname}",
            "task": task
        }

        await self.__repo.update_contest_table_result(contest, table)

    async def delete_user_in_contest(self, id_user: int, uuid_contest: str):
        contest = await self.__repo.get_contest_by_uuid(uuid_contest)
        await self.__repo.delete_user_in_contest(id_user, contest.id)
        table = contest.table_result
        try:
            del table[str(id_user)]
        except KeyError:
            del table[int(id_user)]
        await self.__repo.update_contest_table_result(contest, table)

    async def get_contest_controller(self, uuid_contest: str):
        contest = await self.__repo.get_contest_by_uuid(uuid_contest)
        return ContestUserAndTask.model_validate(contest, from_attributes=True)
