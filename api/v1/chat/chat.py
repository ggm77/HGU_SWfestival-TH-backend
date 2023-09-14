from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from lib.lib import *
from lib.schema import *

router = APIRouter(prefix="/api/v1")


@router.post("/chat")
async def create_chat_room(postData: createchatroomRequest):

    userNumber = await decodeToken(postData.access_token, postData.refresh_token)
    
    if((await getPostInfo(postData.postNumber))["postUserNumber"] != postData.postUserNumber):
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
    
    return JSONResponse(value)


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
    
    userNumber = await decodeToken(access_token, refresh_token)

    chatRoomInfo = await getChatRoomInfoDB(chatRoomNumber)

    if(not chatRoomInfo):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get chatRoomInfo from DB."
        )
    
    if(userNumber != str(chatRoomInfo["postUserNumber"]) and userNumber != str(chatRoomInfo["chatterNumber"])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="UserNumber not correct."
        )
    
    chat_access_token = await create_access_token(chatRoomNumber)
    chat_refresh_token = await create_refresh_token(chatRoomNumber)

    return JSONResponse({"chat_access_token":chat_access_token,"token_type":"bearer","chat_refresh_token":chat_refresh_token,"data":chatRoomInfo})



    
