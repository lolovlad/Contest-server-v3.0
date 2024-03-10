from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    server_host: str
    server_port: int

    server_review_host: str
    server_review_port: int
    static_path: str

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600 * 12

    front_end_host: str
    front_end_port: int

    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_db: str
    postgres_password: str
    pgport: int


settings = Settings(_env_file="settings_server_debug.env", _env_file_encoding="utf-8")
