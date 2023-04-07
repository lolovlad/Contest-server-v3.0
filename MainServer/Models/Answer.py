from pydantic import BaseModel


class AnswerGet(BaseModel):
    date_send: str
    id: int
    id_team: int
    id_user: int
    id_task: int
    id_contest: int
    name_compilation: str
    total: str
    time: str
    memory_size: str
    number_test: int
    points: int

    class Config:
        orm_mode = True
