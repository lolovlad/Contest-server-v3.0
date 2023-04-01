import grpc
from grpc.aio import Channel
from .settings import settings


ip_review = f'{settings.server_review_host}:{settings.server_review_port}'


async def get_channel() -> Channel:
    async with grpc.aio.insecure_channel(ip_review) as channel:
        yield channel
