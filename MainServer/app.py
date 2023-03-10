from fastapi import FastAPI
from .Api import router
from fastapi_utils.tasks import repeat_every

from datetime import datetime
from .database import Session

from .tables import Contest
from .Models.Contest import TypeState

app = FastAPI()
app.include_router(router)


@app.on_event("startup")
@repeat_every(seconds=60, wait_first=False)
def switch_contest_state():
    with Session() as session:
        datetime_now = datetime.now()
        contests = session.query(Contest).filter(Contest.state_contest != TypeState.FINISHED).all()
        for contest in contests:
            if contest.state_contest == TypeState.CONFIRMED:
                if contest.datetime_start <= datetime_now:
                    contest.state_contest = TypeState.GOING_ON
            elif contest.state_contest == TypeState.GOING_ON:
                if contest.datetime_end <= datetime_now:
                    contest.state_contest = TypeState.FINISHED
        session.commit()