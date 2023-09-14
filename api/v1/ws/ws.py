from fastapi import APIRouter, HTTPException, status, WebSocket
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from starlette.websockets import WebSocketDisconnect

from lib.lib import *
from lib.schema import *

router = APIRouter(prefix="/api/v1")

"""

Receive token from chat page and start websocket connection
chat 페이지에서 토큰 받은 다음 웹소켓 연결 시작

"""

@router.websocket("/ws")
async def websocketEndpoint(
    websocket: WebSocket,
    chatRoomNumber: int = None,
    access_token: str = None,
    token_type: str = None,
    refresh_token: str = None
    ):

    if(access_token == None or token_type == None or refresh_token == None):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    tokenChatRoomNumber = int(await decodeToken_ws(access_token, refresh_token))

    if((not tokenChatRoomNumber) or str(chatRoomNumber) != tokenChatRoomNumber):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was : {data}")
    except WebSocketDisconnect:
        await websocket.close()

