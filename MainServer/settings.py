from pydantic import BaseSettings


class Settings(BaseSettings):
    server_host: str
    server_port: int

    server_review_host: str
    server_review_port: int

    database_name: str
    static_path: str

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600 * 12


settings = Settings(_env_file="settings_server.env", _env_file_encoding="utf-8")
