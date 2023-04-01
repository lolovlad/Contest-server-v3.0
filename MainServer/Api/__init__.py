from fastapi import APIRouter
from ..Api.login import router as login_router
from ..Api.users import router as user_router
from ..Api.educational_organizations import router as educational_organizations_router
from ..Api.teams import router as team_router
from ..Api.contests import router as contest_router
from ..Api.tasks import router as task_router
from ..Api.user_contest_view import router as user_contest_view_router
from ..Api.compilations import router as compilations_router


router = APIRouter()
router.include_router(login_router)
router.include_router(user_router)
router.include_router(educational_organizations_router)
router.include_router(team_router)
router.include_router(contest_router)
router.include_router(task_router)
router.include_router(user_contest_view_router)
router.include_router(compilations_router)
