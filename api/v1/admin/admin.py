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
    if(info == -1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found."
        )
    elif(info == 0):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User disabled"
        )
    if(info["userType"] == "admin"):
        param = {"userNumber":postData.targetUserNumber, "disabled":True}
        value = await updateUserInfo(param)
        if(value != 0):
            return JSONResponse({"result":"success"})
        else:
            raise HTTPException(
                status_code=status.HTTP_500,
                detail="Failed to update userInfo in DB."
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Require admin account."
        )
        

@router.post("/enableUser")
async def enableUser(postData: enableuserRequest):
    userNumber = await decodeToken(postData.access_token, postData.refresh_token)
    info = await getUserInfo(userNumber)
    if(info == -1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found."
        )
    elif(info == 0):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User disabled"
        )
    if(info["userType"] == "admin"):
        param = {"userNumber":postData.targetUserNumber, "disabled":False}
        value = await updateUserInfo(param)
        if(value != 0):
            return JSONResponse({"result":"success"})
        else:
            raise HTTPException(
                status_code=status.HTTP_500,
                detail="Failed to update userInfo in DB."
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Require admin account."
        )

@router.patch("/user")
async def changeUserInfo(postData: changuserinfoRequest):
    if(await adminVerify(postData.admin_access_token, postData.admin_refresh_token)):
        updateData = jsonable_encoder(postData)

        if(updateData["email"] != None):
            if(await checkUserExist(updateData["email"])):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exist."
                )

        keyList = list(updateData.keys())
        for i in range(len(keyList)):
            if(updateData[keyList[i]] == None):
                del updateData[keyList[i]]
        del updateData["admin_access_token"]
        del updateData["admin_token_type"]
        del updateData["admin_refresh_token"]
        
        value = await updateUserInfo(updateData)
        if(value != 0):
            return JSONResponse({"result":"success"})
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update userInfo in DB."
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Require admin account."
        )

@router.delete("/user")
async def deleteUser():
    return