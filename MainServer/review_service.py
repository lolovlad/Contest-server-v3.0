from httpx import AsyncClient
from .settings import settings


ip_review = f'http://{settings.server_review_host}:{settings.server_review_port}/v1/'


async def get_channel() -> AsyncClient:
    print(ip_review)
    async with AsyncClient(base_url=ip_review) as client:
        yield client
