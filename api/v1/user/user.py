from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from lib.lib import *
from lib.dataClass import *

router = APIRouter(prefix="/api/v1")


@router.post("/user")
async def createAccount(postData: registRequest):

    if(await checkUserExist(postData.email)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=postData.email + " is already exist in DB."
        )

    user = await registUser(jsonable_encoder(postData))

    if(user):
        del user["hashed_password"]
        return JSONResponse(jsonable_encoder(user))
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Regist user failed."
        )
    

@router.get("/user")
async def getUserinfo(access_token: str, token_type: str, refresh_token: str):
    payload = await decodeToken(access_token, refresh_token)
    userNumber = payload.get("sub")
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

    if(payload.get("type")=="refresh"):
        return JSONResponse({"data":jsonable_encoder(user),"token":await create_token(payload.get("sub"))})
    else:
        return JSONResponse({"data":jsonable_encoder(user),"token":{"access_token":access_token,"refresh_token":refresh_token}})
    

@router.patch("/user")
async def updateUserinfo(putData: updateuserRequest):
    payload = await decodeToken(putData.access_token, putData.refresh_token)
    userNumber = payload.get("sub")
    info = await getUserInfo(userNumber)
    if(info == -2):
        await raiseDBDownError()
    elif(info == -1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found."
        )
    elif(info == 0):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User disabled"
        )
    
    putData = jsonable_encoder(putData)

    if(putData["email"] != None and putData["email"] != info["email"]):
        if(await checkUserExist(putData["email"])):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email aready exist."
            )
        
    if(putData["password"] != None):
        putData["hashed_password"] = getHashedPassword(putData["password"])
        del putData["password"]

    keyList = list(putData.keys())
    for i in range(len(keyList)):
        if(putData[keyList[i]] == None):
            del putData[keyList[i]]

    
    
    putData["userNumber"] = userNumber
    access_token = putData["access_token"]
    refresh_token = putData["refresh_token"]
    del putData["access_token"]
    del putData["token_type"]
    del putData["refresh_token"]
    value = await updateUserInfo(putData)
    if(value == -2):
        await raiseDBDownError()
    user = await getUserInfo(value)
    if(user == -2):
        await raiseDBDownError()
    if(value != 0):
        if(payload.get("type")=="refresh"):
            return JSONResponse({"data":user,"token":await create_token(payload.get("sub"))})
        else:
            return JSONResponse({"data":user,"token":{"access_token":access_token,"refresh_token":refresh_token}})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Faild to update userInfo in DB."
        )


@router.delete("/user")
async def deleteUser(deleteData: deleteuserRequest):
    authUser = await authenticate_user(deleteData.email, deleteData.password)
    if(authUser == 1):
        userNumber = await emailToUserNumber(deleteData.email)
        payload = await decodeToken(deleteData.access_token, deleteData.refresh_token)
        if(str(userNumber) == payload.get("sub")):
            value = await deleteUserInfo(userNumber)
            if(value == -2):
                await raiseDBDownError()
            userPicture = await getUserPictureDB(userNumber)
            if(userPicture == -2):
                await raiseDBDownError()
            elif(userPicture):
                isDeletedInAzure = await deleteUserProfilePicture_azure(userNumber)
                if(isDeletedInAzure):
                    isDeleted = await deleteUserProfilePictureURL_DB(userNumber)
                    if(isDeleted == -2):
                        await raiseDBDownError()
                    elif(not isDeleted):
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to delete picture from DB. (userInfo deleted in DB, userProfilePicture deleted in Azure)"
                        )

            if(value == 1):
                if(payload.get("type")=="refresh"):
                    return JSONResponse({"data":{"result":"success"},"token":await create_token(payload.get("sub"))})
                else:
                    return JSONResponse({"data":{"result":"success"},"token":{"access_token":deleteData.access_token,"refresh_token":deleteData.refresh_token}})
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete userInfo in DB."
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token authorize or email authorize error.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    elif(authUser == -1):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif(authUser == 0):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password not correct.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorize error.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    