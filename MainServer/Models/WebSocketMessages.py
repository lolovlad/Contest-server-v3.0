from pydantic import BaseModel
from enum import Enum
from typing import List
from .User import UserGet


class TypePool(str, Enum):
    ANSWER = "answer"
    TABLE = "table"


class TypeMessage(str, Enum):
    SUBSCRIBE_TABLE = "subscribe_table"
    SUBSCRIBE_ANSWER = "subscribe_answer"
    ANSWER_UPDATE = "answer_update"
    UNSUBSCRIBE_TABLE = "unsubscribe_table"
    UNSUBSCRIBE_ANSWER = "unsubscribe_answer"


class User(BaseModel):
    user: UserGet | None
    websocket: object


class BaseMessage(BaseModel):
    type_message: TypeMessage
    body_message: dict
