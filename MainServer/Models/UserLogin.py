from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    type_user: int


class UserSigIn(BaseModel):
    type_user: int
    token: Token


class UserLogin(BaseModel):
    login: str
    password: str


