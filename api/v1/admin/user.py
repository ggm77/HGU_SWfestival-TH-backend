from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from lib.lib import *
from lib.schema import *


router = APIRouter(prefix="/api/v1/admin")

@router.post("/disableUser")
async def disableUser(postData: disableuserRequest):
    tokenDict = await adminVerify(postData.access_token, postData.refresh_token)
    param = {"userNumber":postData.targetUserNumber, "disabled":True}
    value = await updateUserInfo(param)
    if(value == -2):
        await raiseDBDownError()
    if(value != 0):
        return JSONResponse({"data":{"result":"success"},"token":tokenDict})
    else:
        raise HTTPException(
            status_code=status.HTTP_500,
            detail="Failed to update userInfo in DB."
        )

        

@router.post("/enableUser")
async def enableUser(postData: enableuserRequest):
    tokenDict = await adminVerify(postData.access_token, postData.refresh_token)
    param = {"userNumber":postData.targetUserNumber, "disabled":False}
    value = await updateUserInfo(param)
    if(value == -2):
        await raiseDBDownError()
    elif(value != 0):
        return JSONResponse({"data":{"result":"success"},"token":tokenDict})
    else:
        raise HTTPException(
            status_code=status.HTTP_500,
            detail="Failed to update userInfo in DB."
        )
    
@router.delete("/user/picture")
async def deleteUserPicture(deleteData: deleteuserpicture_adminRequest):
    tokenDict = await adminVerify(deleteData.access_token, deleteData.refresh_token)
    isDeleted = await deleteUserProfilePicture(deleteData.userNumber)
    if(isDeleted == -2):
        await raiseDBDownError()
    elif(isDeleted):
        return JSONResponse({"data":{"result":"success"},"token":tokenDict})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete picture from DB."
        )
    
@router.get("/user/{userNumber}")
async def getUserinfo(userNumber: int, access_token: str, token_type: str, refresh_token: str):
    tokenDict = await adminVerify(access_token, refresh_token)
    user = await getUserInfo(userNumber)
    if(user == -2):
        await raiseDBDownError()
    elif(user == -1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found."
        )
    elif(user == 0):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User disabled"
        )

    del user["hashed_password"]

    return JSONResponse({"data":jsonable_encoder(user),"token":tokenDict})
    

@router.patch("/user")
async def changeUserInfo(postData: changuserinfoRequest):
    tokenDict = await adminVerify(postData.admin_access_token, postData.admin_refresh_token)
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
    if(value == -2):
        await raiseDBDownError()
    elif(value != 0):
        return JSONResponse({"data":{"result":"success"},"token":tokenDict})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update userInfo in DB."
        )


@router.delete("/user")
async def deleteUser(deleteData: deleteuser_adminRequest):
    tokenDict = await adminVerify(deleteData.access_token, deleteData.refresh_token)
    value = await deleteUserInfo(deleteData.targetUserNumber)
    if(value == -2):
        await raiseDBDownError()
    userPicture = await getUserPictureDB(deleteData.targetUserNumber)
    if(userPicture == -2):
        await raiseDBDownError()
    elif(userPicture):
        isDeleted = await deleteUserProfilePicture(deleteData.targetUserNumber)
        if(isDeleted == -2):
            await raiseDBDownError()
        elif(not isDeleted):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete picture from DB."
            )
    if(value == 1):
        return JSONResponse({"data":{"result":"success"},"token":tokenDict})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete userInfo in DB."
        )

