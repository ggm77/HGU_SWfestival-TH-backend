import socketio

from lib.lib import *


#https://velog.io/@stresszero/python-socketio


sio_server = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=[]
)

sio_app = socketio.ASGIApp(
    socketio_server=sio_server,
    socketio_path='sockets'
)


@sio_server.event
async def connect(sid, environ, auth: dict):


    """
    ----frontend (react)----
    const socket = io("http://localhost:64000", {
        path: "/api/v1/socket_IO/sockets",
        auth: {
            access_token: access_token,
            refresh_token: refresh_token,
            chat_access_token: chat_access_token,
            chat_refresh_token: chat_refresh_token,
            token_type: "bearer",
            room: "2:1->2" // '채팅방 번호' : '채팅 건 사람' -> '원본 포스팅 쓴 사람'     'chatRoomNumber' : 'chatterNumber' -> 'postUserNumber'
        }
        });
    """

    
    chat_payload = await decodeToken_ws(auth["chat_access_token"], auth["chat_refresh_token"])
    if(chat_payload == False):
        return False

    chatRoomNumber = chat_payload.get("sub")
    if(chatRoomNumber != auth["room"]):
        return False

    payload = await decodeToken_ws(auth["access_token"], auth["refresh_token"])
    if(payload == False):
        return False
    
    userNumber = payload.get("sub")

    sio_server.save_session(sid, chatRoomNumber)
    sio_server.enter_room(sid, chatRoomNumber)

    print(f'{sid}: connected')
    await sio_server.emit('join', {'sid': sid}, to=chatRoomNumber)


@sio_server.event
async def chat(sid, data, room):

    """
    data = {
        "messageType":"(message or jpeg)",
        "message":"(메세지 or null)",
        "file":"(null or 파일 or null)",
        "timestamp":"2023.10.10T22:42:20"
    }
    """
    if(data["messageType"] == "message"):
        await sio_server.emit('chat', {'sid' : sid, 'messageType' : 'message', 'message': data["message"]}, to=room)

    elif(data["messageType"] == "jpeg"):
        # 채팅 저장 여부에 따라 이미지 저장 
        await sio_server.emit('chat', {'sid' : sid, 'messageType' : 'jpeg', 'file':data["file"]}, to=room)


@sio_server.event
async def disconnect(sid):
    print(f'{sid}: disconnected')

@sio_server.event
async def leave(sid, room):
    await sio_server.emit('chat', {'sid' : sid, 'messageType' : 'info', 'info' : f'[{sid} has left]'}, to=room)
    sio_server.leave_room(sid, room)