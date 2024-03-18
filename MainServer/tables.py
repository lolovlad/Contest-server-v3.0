from sqlalchemy import Column, Integer, String, LargeBinary, \
    DateTime, ForeignKey, Boolean, Text, Float, UUID

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict

from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4

base = declarative_base()


class TypeUser(base):
    __tablename__ = "type_user"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(32), nullable=False)
    description = Column(String(128), nullable=True)


class User(base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)

    login = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    id_type = Column(Integer, ForeignKey("type_user.id"))
    type = relationship("TypeUser", lazy="joined")

    name = Column(String, nullable=True)
    sename = Column(String, nullable=True)
    secondname = Column(String, nullable=True)
    foto = Column(String, nullable=True, default="Photo/default.png")

    id_edu_organization = Column(Integer, ForeignKey("educational_organizations.id"), nullable=True)
    edu_organization = relationship("EducationalOrganizations", lazy="joined")
    stage_edu = Column(String, nullable=True)

    data = Column(MutableDict.as_mutable(JSONB), default={})

    last_datatime_sign = Column(DateTime, nullable=True)
    last_ip_sign = Column(String, nullable=True)

    #contests = relationship("Contest",
    #                        secondary="contest_registration",
    #                        cascade="all, delete",
    #                        lazy="joined")
    @property
    def password(self):
        return self.hashed_password

    @password.setter
    def password(self, val):
        self.hashed_password = generate_password_hash(val)

    def check_password(self, password):
        if self.type.name == "admin":
            return check_password_hash(self.hashed_password, password)
        else:
            return password == self.hashed_password


class TypeOrganizations(base):
    __tablename__ = "type_organizations"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(32), nullable=False)
    start_range = Column(Integer, nullable=False, default=1)
    end_range = Column(Integer, nullable=False, default=3)
    postfix = Column(String(10), nullable=True)
    description = Column(String(128), nullable=True)


class EducationalOrganizations(base):
    __tablename__ = "educational_organizations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID, nullable=False, default=uuid4())
    name_organizations = Column(String, nullable=False)
    type_organizations_id = Column(Integer, ForeignKey("type_organizations.id"))
    type_organizations = relationship("TypeOrganizations", lazy="joined")


class ContestRegistration(base):
    __tablename__ = "contest_registration"

    id_user = Column(ForeignKey('user.id'), primary_key=True)
    id_contest = Column(ForeignKey('contest.id'), primary_key=True)
    state_contest = Column(Integer, nullable=False, default=1)
    contest = relationship("Contest", lazy="joined")


class TypeContest(base):
    __tablename__ = "type_contest"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(32), nullable=False)
    description = Column(String(128), nullable=True)


class StateContest(base):
    __tablename__ = "state_contest"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(32), nullable=False)
    description = Column(String(128), nullable=True)


class Contest(base):
    __tablename__ = "contest"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID, nullable=False, default=uuid4())
    name_contest = Column(String, nullable=True)
    datetime_start = Column(DateTime, nullable=True)
    datetime_end = Column(DateTime, nullable=True)

    description = Column(LargeBinary, nullable=True, default=b'')
    datetime_registration = Column(DateTime, default=datetime.now())

    id_type = Column(Integer, ForeignKey("type_contest.id"))
    type = relationship("TypeContest", lazy="joined")
    id_state_contest = Column(Integer, ForeignKey("state_contest.id"))
    state_contest = relationship("StateContest", lazy="joined")

    users = relationship("User", lazy="joined", cascade="all, delete", secondary="contest_registration")
    tasks = relationship("Task", lazy="joined", cascade="all, delete", secondary="contest_to_task")


class TypeTask(base):
    __tablename__ = "type_task"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(32), nullable=False)
    description = Column(String(128), nullable=True)


class ContestToTask(base):
    __tablename__ = "contest_to_task"
    id_contest = Column(ForeignKey("contest.id"), primary_key=True)
    id_task = Column(ForeignKey("task.id"), primary_key=True)


class Task(base):
    __tablename__ = "task"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID, nullable=False, default=uuid4())
    name_task = Column(String, nullable=False)

    description = Column(LargeBinary, nullable=False)
    description_input = Column(LargeBinary, nullable=True, default=None)
    description_output = Column(LargeBinary, nullable=True, default=None)

    id_type_task = Column(Integer, ForeignKey("type_task.id"))
    type_task = relationship("TypeTask", lazy="joined")
    complexity = Column(Integer, default=1)
    #answers = relationship("Answer", backref="task", lazy=True)
