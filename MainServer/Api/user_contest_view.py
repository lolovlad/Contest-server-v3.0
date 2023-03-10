from fastapi import WebSocket, WebSocketDisconnect, WebSocketException, APIRouter, Depends, Query
from fastapi import status
from ..Services.WebSocketManager import ConnectionManager
from ..Services.LoginServices import get_current_user

router = APIRouter(prefix="/user_contest_view")


async def get_token(
    websocket: WebSocket,
    token: str = Query(default=None),
):
    if token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    return token


@router.websocket("/view_contest")
async def view_contest(websocket: WebSocket, manager: ConnectionManager = Depends(),
                       token: str = Depends(get_token)):
    await manager.connect(websocket, token)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.receive(data, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)