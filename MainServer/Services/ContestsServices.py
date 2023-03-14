from fastapi import Depends, HTTPException
from ..Models.Contest import ContestGet, ContestPost, ContestDelete, UserContest, \
    ContestPutUsers, ContestUpdate, ContestCardView, TypeState, TypeContest
from ..Models.User import StateUser
from ..Models.ReportTotal import ReportTotal
from typing import List

from sqlalchemy.orm import Session
from ..tables import Contest, ContestRegistration, User, Team
from ..database import get_session
from ..settings import settings

from datetime import timedelta, datetime
from json import loads

from .TaskServices import TaskServices

import grpc
from .protos import contest_pb2, contest_pb2_grpc


class ContestsServices:
    def __init__(self, session: Session = Depends(get_session)):
        self.__session: Session = session
        self.__time_zone = timedelta(hours=4)
        self.__ip_review = f'{settings.server_review_host}:{settings.server_review_port}'

    def __get_by_id(self, id_contest: int) -> Contest:
        return self.__session.query(Contest).filter(Contest.id == id_contest).first()

    def __get_reg_users(self, id_contest: int) -> List[ContestRegistration]:
        users = self.__session.query(ContestRegistration).filter(ContestRegistration.id_contest == id_contest).all()
        return users

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
                                 datetime_start=contest.datetime_start - self.__time_zone,
                                 datetime_end=contest.datetime_end - self.__time_zone,
                                 datetime_registration=contest.datetime_registration - self.__time_zone,
                                 type=contest.type,
                                 state_contest=contest.state_contest,
                                 tasks=[])
        return contest_reg

    def get_list_contest(self) -> List[ContestGet]:
        contests = self.__session.query(Contest).all()
        contest_reg = []
        for contest in contests:
            contest_reg.append(self.__convert_contest(contest))
        return contest_reg

    def get_contest(self, id_contest: int) -> ContestGet:
        return self.__convert_contest(self.__get_by_id(id_contest))

    def add_contest(self, contest_data: ContestPost) -> ContestGet:
        contest = Contest(name_contest=contest_data.name_contest,
                          datetime_start=datetime.strptime(contest_data.datetime_start, '%Y-%m-%dT%H:%M:%S.%fZ') + self.__time_zone,
                          datetime_end=datetime.strptime(contest_data.datetime_end, '%Y-%m-%dT%H:%M:%S.%fZ') + self.__time_zone,
                          type=contest_data.type,
                          state_contest=contest_data.state_contest)

        self.__session.add(contest)
        self.__session.commit()
        contest = self.__convert_contest(contest)
        return contest

    def delete_contest(self, id_contest: int) -> ContestDelete:
        contest = self.__get_by_id(id_contest)
        ts_service = TaskServices()
        if contest.tasks is not None:
            for task in contest.tasks:
                ts_service.delete_task(task.id)
        self.__session.delete(contest)
        self.__session.commit()
        contest = ContestDelete(id=contest.id,
                                name_contest=contest.name_contest,
                                datetime_start=contest.datetime_start,
                                datetime_end=contest.datetime_end,
                                datetime_registration=contest.datetime_registration,
                                type=contest.type,
                                state_contest=contest.type)
        return contest

    def update_contest(self, contest_data: ContestUpdate) -> ContestGet:
        contest = self.__get_by_id(contest_data.id)
        for field, val in contest_data:
            if field in ("name_contest", "state_contest"):
                setattr(contest, field, val)
            elif field in ("datetime_start", "datetime_end"):
                setattr(contest, field, datetime.strptime(val, '%Y-%m-%dT%H:%M:%S.%fZ') + self.__time_zone)
        self.__session.commit()
        contest = self.__get_by_id(contest.id)
        contest = self.__convert_contest(contest)
        return contest

    def add_users_contest(self, contest_data: ContestPutUsers) -> ContestGet:
        contest = self.__get_by_id(contest_data.id)
        users = self.__get_reg_users(contest_data.id)
        for user in users:
            self.__session.delete(user)
        for user in contest_data.users:
            if user.id_team == 0:
                user.id_team = None
            contest_reg = ContestRegistration(id_user=user.id,
                                              id_contest=contest.id,
                                              id_team=user.id_team)
            self.__session.add(contest_reg)
        self.__session.commit()
        contest = self.__convert_contest(contest)
        return contest

    def get_list_contest_by_user_id(self, id_user: int) -> List[ContestCardView]:
        contests_reg = self.__session.query(ContestRegistration).filter(ContestRegistration.id_user == id_user).all()
        card_view = []
        for contest_registration in contests_reg:
            is_view = True

            if contest_registration.state_contest == StateUser.BANNED:
                is_view = False

            if contest_registration.contest.state_contest != TypeState.GOING_ON:
                is_view = False

            card_view.append(ContestCardView(
                id=contest_registration.id_contest,
                name_contest=contest_registration.contest.name_contest,
                type=contest_registration.contest.type,
                state_contest=contest_registration.contest.state_contest,
                is_view=is_view
            ))
        return card_view

    async def get_report_total(self, id_contest: int) -> List[ReportTotal]:
        contest = self.__get_by_id(id_contest)
        async with grpc.aio.insecure_channel(self.__ip_review) as channel:
            sub = contest_pb2_grpc.ContestApiStub(channel)
            request = contest_pb2.GetReportTotalRequest(id_contest=id_contest)
            response = await sub.GetReportTotal(request)
        if contest.type == TypeContest.OLIMPIADA:
            set_id = self.__session.query(ContestRegistration.id_user).\
                distinct(ContestRegistration.id_user).\
                filter(ContestRegistration.id_contest == id_contest).all()

        else:
            set_id = self.__session.query(ContestRegistration.id_team).\
                distinct(ContestRegistration.id_team).\
                filter(ContestRegistration.id_contest == id_contest).all()
        reports = []
        result = loads(response.result.decode())
        for id_entity in set_id:
            name = ""
            if contest.type == TypeContest.OLIMPIADA:
                user = self.__session.query(User).filter(User.id == id_entity[0]).first()
                name = f"{user.sename} {user.name[0]}. {user.secondname[0]}."
            else:
                team = self.__session.query(Team).filter(Team.id == id_entity[0]).first()
                name = team.name_team

            if str(id_entity[0]) not in result:
                reports.append(ReportTotal(
                    name_contest=contest.name_contest,
                    type_contest=contest.type,
                    name=name,
                    total={str(entity.id): 0 for entity in contest.tasks},
                    sum_point=0
                ))
            else:
                target_res = result[str(id_entity[0])]
                for task in contest.tasks:
                    if str(task.id) not in target_res["total"]:
                        target_res["total"][str(task.id)] = 0
                target_res["name_contest"] = contest.name_contest
                target_res["name"] = name
                reports.append(ReportTotal(**target_res))
        return reports