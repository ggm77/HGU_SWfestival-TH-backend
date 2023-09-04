from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from lib.lib import *
from lib.schema import *


router = APIRouter(prefix="/api/v1/admin")

@router.post("/disableUser")
async def disableUser(postData: disableuserRequest):
    await adminVerify(postData.access_token, postData.refresh_token)
    param = {"userNumber":postData.targetUserNumber, "disabled":True}
    value = await updateUserInfo(param)
    if(value != 0):
        return JSONResponse({"result":"success"})
    else:
        raise HTTPException(
            status_code=status.HTTP_500,
            detail="Failed to update userInfo in DB."
        )

        

@router.post("/enableUser")
async def enableUser(postData: enableuserRequest):
    await adminVerify(postData.access_token, postData.refresh_token)
    param = {"userNumber":postData.targetUserNumber, "disabled":False}
    value = await updateUserInfo(param)
    if(value != 0):
        return JSONResponse({"result":"success"})
    else:
        raise HTTPException(
            status_code=status.HTTP_500,
            detail="Failed to update userInfo in DB."
        )

@router.patch("/user")
async def changeUserInfo(postData: changuserinfoRequest):
    await adminVerify(postData.admin_access_token, postData.admin_refresh_token)
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


@router.delete("/user")
async def deleteUser(deleteData: deleteuser_adminRequest):
    await adminVerify(deleteData.access_token, deleteData.refresh_token)
    value = await deleteUserInfo(deleteData.targetUserNumber)
    if(value == 1):
        return JSONResponse({"result":"success"})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete userInfo in DB."
        )

