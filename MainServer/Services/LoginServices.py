from jose import JWTError, jwt

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..tables import User
from ..Models.User import UserGet, TypeUser
from ..Models.UserLogin import UserLogin, Token, UserSigIn
from ..database import get_session
from ..settings import settings
from datetime import datetime, timedelta

oauth2_cheme = OAuth2PasswordBearer(tokenUrl='/login/sign-in/')


def get_current_user(token: str = Depends(oauth2_cheme)) -> UserGet:
    return LoginServices.validate_token(token)


class LoginServices:
    def __init__(self, session: Session = Depends(get_session)):
        self.__session = session

    def __get(self, login_user: str) -> User:
        user = self.__session.query(User).filter(User.login == login_user).first()
        return user

    @classmethod
    def validate_token(cls, token: str) -> UserGet:
        exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                  detail="token",
                                  headers={
                                      "AGUContest": 'Bearer'
                                  })
        try:
            payload = jwt.decode(token,
                                 settings.jwt_secret,
                                 algorithms=[settings.jwt_algorithm])
        except JWTError:
            raise exception

        user_data = payload.get("user")

        try:
            user = UserGet.parse_obj(user_data)
        except Exception:
            raise exception
        return user

    @classmethod
    def create_token(cls, user: User) -> Token:
        user_data = UserGet.from_orm(user)

        now = datetime.utcnow()

        payload = {
            'iat': now,
            'nbf': now,
            'exp': now + timedelta(seconds=settings.jwt_expiration),
            'sub': str(user_data.id),
            'user': user_data.dict()
        }
        token = jwt.encode(payload,
                           settings.jwt_secret,
                           algorithm=settings.jwt_algorithm)
        return Token(access_token=token, type_user=user_data.type)

    def login_user(self, user_login: UserLogin, request: Request) -> Token:
        user = self.__get(user_login.login)
        if user:
            if user.check_password(user_login.password):
                user.last_datatime_sign = datetime.now()
                user.last_ip_sign = request.client.host
                self.__session.commit()
                return self.create_token(user)