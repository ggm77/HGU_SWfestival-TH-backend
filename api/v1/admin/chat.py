from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from lib.lib import *
from lib.dto import *

router = APIRouter(prefix="/api/v1/admin")


@router.delete("/chat")
async def delete_chat_room(deleteData: deletechatroom_adminRequest):
    tokenDict = await adminVerify(deleteData.access_token, deleteData.refresh_token)

    isDeleted = await deleteChatRoomInfoDB(deleteData.chatRoomNumber)
    if(isDeleted == -2):
        await raiseDBDownError()
    elif(isDeleted):
        return JSONResponse({"data":{"result":"success"}, "token":tokenDict})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete chatRoom in DB."
        )