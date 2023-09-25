from fastapi import APIRouter, HTTPException, status, WebSocket
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from starlette.websockets import WebSocketDisconnect

from lib.lib import *
from lib.schema import *

from datetime import timedelta, datetime
import asyncio
from multiprocessing import Process


router = APIRouter(prefix="/api/v1")


"""

Receive token from chat page and start websocket connection
chat 페이지에서 토큰 받은 다음 웹소켓 연결 시작

You must receive the message number from the front desk.
메세지 번호를 프론트에서 받아야함

Chatting is done on the front end.
채팅 받는건 프론트엔드에서

"""


@router.websocket("/ws/createchat")
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
    
    
    await websocket.accept()
    
    try:
        # change all of "readChat" to True
        
        while True:
            data = await websocket.receive_text()
            index2 = data.find("|")
            if(index2 == -1):
                await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
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

            await createChat(tokenChatRoomNumber+"."+str(tokenUserNumber),str(sendData))
            await backupChat(str(sendData))
            
            
    except WebSocketDisconnect:
        await websocket.close()

#client is get chat for rabbitmq directly!
#not use
# @router.websocket("/ws/getchat")
# async def get_chat_ws(
#     websocket: WebSocket,
#     chatRoomNumber: int = None,
#     chat_access_token: str = None,
#     token_type: str = None,
#     chat_refresh_token: str = None
# ):
#     if(chat_access_token == None or token_type == None or chat_refresh_token == None):
#         await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
#         return
    
    
#     tokenChatRoomNumberAndUserNumber = await decodeToken_ws(chat_access_token, chat_refresh_token)
#     if(tokenChatRoomNumberAndUserNumber == False):
#         await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
#         return
#     index = tokenChatRoomNumberAndUserNumber.find("-")
#     tokenChatRoomNumber = tokenChatRoomNumberAndUserNumber[:index]
#     tokenUserNumber = int(tokenChatRoomNumberAndUserNumber[index+1:])
    
#     if((not tokenChatRoomNumber) or str(chatRoomNumber) != tokenChatRoomNumber):
#         await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
#         return
    
    
#     await websocket.accept()

#     async def on_message(ch, method_frame, header_frame, body):
#         try:
#             print(f"message : {body}")
#             await websocket.send_text(f"sended data : {body}")
#         except KeyboardInterrupt:
#             print("stop")
#             ch.stop_consuming()


#     try:
#         # while True:
#         result = await getChat(tokenChatRoomNumberAndUserNumber, on_message)
#         print(result)
#         await websocket.send_text(f"sended data : {result}")

#     except WebSocketDisconnect:
#         await websocket.close()



