from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from lib.lib import *
from lib.schema import *


router = APIRouter(prefix="/api/v1/admin")

@router.post("/disableUser")
async def disableUser(postData: disableuserRequest):
    userNumber = await decodeToken(postData.access_token, postData.refresh_token)
    info = await getUserInfo(userNumber)
    if(info["userType"] == "admin"):
        param = {"userNumber":postData.targetUserNumber, "disabled":True}
        value = await updateUserInfo(param)
        if(value != 0):
            return {"result":"success"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500,
                detail="Failed to update userInfo in DB."
            )
        

@router.post("/enableUser")
async def enableUser(postData: enableuserRequest):
    userNumber = await decodeToken(postData.access_token, postData.refresh_token)
    info = await getUserInfo(userNumber)
    if(info["userType"] == "admin"):
        param = {"userNumber":postData.targetUserNumber, "disabled":False}
        value = await updateUserInfo(param)
        if(value != 0):
            return {"result":"success"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500,
                detail="Failed to update userInfo in DB."
            )

@router.put("/user")
async def changeUserInfo(postData):
    return
