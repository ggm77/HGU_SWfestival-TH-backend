from fastapi import APIRouter, HTTPException, status, WebSocket
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from starlette.websockets import WebSocketDisconnect

from lib.lib import *
from lib.schema import *

from datetime import timedelta, datetime
import asyncio


router = APIRouter(prefix="/api/v1")


"""

Receive token from chat page and start websocket connection
chat 페이지에서 토큰 받은 다음 웹소켓 연결 시작

"""


@router.websocket("/ws")
async def create_chat_ws(
    websocket: WebSocket,
    chatRoomNumber: int = None,
    chat_access_token: str = None,
    token_type: str = None,
    chat_refresh_token: str = None
    ):


    if(chat_access_token == None or token_type == None or chat_refresh_token == None):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    
    tokenChatRoomNumberAndUserNumber = await decodeToken_ws(chat_access_token, chat_refresh_token)
    if(tokenChatRoomNumberAndUserNumber == False):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    index = tokenChatRoomNumberAndUserNumber.find("-")
    tokenChatRoomNumber = tokenChatRoomNumberAndUserNumber[:index]
    tokenUserNumber = int(tokenChatRoomNumberAndUserNumber[index+1:])
    
    if((not tokenChatRoomNumber) or str(chatRoomNumber) != tokenChatRoomNumber):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # chatRoomInfo = 
    
    await websocket.accept()
    try:
        
        while True:
            result = await getChat(tokenChatRoomNumberAndUserNumber)
            print(result)
            data = await websocket.receive_text()
            index2 = data.find("|")
            messageNumber = data[:index2]
            data = data[index2+1:]
            sendData = {
                "chatRoomNumber":chatRoomNumber,
                "messageNumber":messageNumber,
                "authorUserNumber":tokenUserNumber,
                "text":data,
                "date":datetime.now(),
                "readChat":False
            }
            await createChat(tokenChatRoomNumberAndUserNumber,str(sendData))
            
            await websocket.send_text(f"sended data : {result}")
            
    except WebSocketDisconnect:
        await websocket.close()


