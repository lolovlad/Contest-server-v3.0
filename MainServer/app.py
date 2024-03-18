from fastapi import FastAPI
from .Api import router
from .settings import settings
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every
from MainServer.async_database import async_session
from .tables import Contest, StateContest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import datetime

app = FastAPI()
app.include_router(router)


origins = [
    f"http://{settings.front_end_host}:{settings.front_end_port}",
    f"http://{settings.front_end_host}",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Count-Page", "X-Count-Item-User", "X-Count-Item"],
)


@app.on_event("startup")
@repeat_every(seconds=60)
async def switch_contest_state() -> None:
    async with async_session() as session:
        datetime_now = datetime.now()

        query = select(Contest).join(StateContest).where(StateContest.name != "completed")
        response = await session.execute(query)
        contests = response.unique().scalars().all()

        for contest in contests:
            if contest.state_contest.name == "confirmed":
                if contest.datetime_start <= datetime_now:
                    contest.id_state_contest = 3
            elif contest.state_contest.name == "passes":
                if contest.datetime_end <= datetime_now:
                    contest.id_state_contest = 4
        await session.commit()
