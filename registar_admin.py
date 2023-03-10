from MainServer.database import Session
from MainServer.tables import User

session = Session()

user_data = {
    "login": "admin",
    "password": "admin",
    "type": 1,
    "name": "Vlad",
    "sename": "Skripnik",
    "secondname": "Vicktor"
}

user = User(**user_data)
user.password = user_data["password"]
session.add(user)
session.commit()