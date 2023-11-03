from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from lib.lib import *
from lib.dataClass import *

router = APIRouter(prefix="/api/v1")


@router.post("/chat")#마지막 채팅번호 리턴
async def create_chat_room(postData: createchatroomRequest):

    payload = await decodeToken(postData.access_token, postData.refresh_token)
    userNumber = payload.get("sub")
    info = await getPostInfo(postData.postNumber)
    print(info)
    if(info == -2):
        await raiseDBDownError()
    elif(info == -1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Posting not exist."
        )
    elif(info == 0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Posting was disabled."
        )
    elif(info["postUserNumber"] != postData.postUserNumber):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="PostUserNumber not matched"
        )
    
    postData = jsonable_encoder(postData)
    postData["userNumber"] = userNumber
    
    value = await createChatRoom(jsonable_encoder(postData))

    if(not value):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to creatChatRoom."
        )
    
    if(payload.get("type")=="refresh"):
        return JSONResponse({"data":value,"token":await create_token(userNumber)})
    else:
        return JSONResponse({"data":value,"token":{"access_token":postData["access_token"],"refresh_token":postData["refresh_token"]}})


@router.get("/chat")
async def get_chat_room(
    chatRoomNumber: int = None,
    access_token: str = None,
    token_type: str = None,
    refresh_token: str = None
):
    if(chatRoomNumber == None or access_token == None or token_type == None or refresh_token == None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parameters are not satisfied."
        )
    
    payload = await decodeToken(access_token, refresh_token)
    userNumber = payload.get("sub")

    chatRoomInfo = await getChatRoomInfoDB(chatRoomNumber)
    if(chatRoomInfo == -2):
        await raiseDBDownError()
    elif(not chatRoomInfo):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get chatRoomInfo from DB."
        )
    
    if(userNumber != str(chatRoomInfo["postUserNumber"]) and userNumber != str(chatRoomInfo["chatterNumber"])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="UserNumber not correct."
        )
    # 2:1->2
    #'채팅방 번호' : '채팅 건 사람' -> '원본 포스팅 쓴 사람'     'chatRoomNumber' : 'chatterNumber' -> 'postUserNumber'
    chat_access_token = await create_access_token(str(chatRoomNumber)+":"+str(chatRoomInfo["chatterNumber"])+"->"+str(chatRoomInfo["postUserNumber"]))
    chat_refresh_token = await create_refresh_token(str(chatRoomNumber)+":"+str(chatRoomInfo["chatterNumber"])+"->"+str(chatRoomInfo["postUserNumber"]))

    # await chatSetup(str(chatRoomNumber)+"."+str(userNumber))
    # await chatRecodeSetup()

    if(payload.get("type")=="refresh"):
        return JSONResponse(
            {
                "data":
                {
                    "chat_access_token":chat_access_token,
                    "token_type":"bearer",
                    "chat_refresh_token":chat_refresh_token,
                    "data":chatRoomInfo
                },
                "token":await create_token(userNumber)
            }
        )
    else:
        return JSONResponse(
            {
                "data":
                {
                    "chat_access_token":chat_access_token,
                    "token_type":"bearer",
                    "chat_refresh_token":chat_refresh_token,
                    "data":chatRoomInfo
                },
                "token":{
                    "access_token":access_token,
                    "refresh_token":refresh_token
                }
            }
        )



    
