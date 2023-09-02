from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from lib.lib import *
from lib.lib import authenticate_user
from lib.schema import *
from lib.schema import registRequest

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
    

@router.get("/user/")
async def getUserinfo(access_token: str, token_type: str, refresh_token: str):
    userNumber = await decodeToken(access_token, refresh_token)
    user = await getUserInfo(userNumber)
    if(not user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not found or user disabled."
        )
    del user["hashed_password"]

    return JSONResponse(jsonable_encoder(user))
    

@router.put("/user")
async def updateUserinfo(putData: updateuserRequest):
    userNumber = await decodeToken(putData.access_token, putData.refresh_token)
    info = await getUserInfo(userNumber)
    if(putData.email != info["email"]):
        if(await checkUserExist(putData.email)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email aready exist."
            )
    putData = jsonable_encoder(putData)
    putData["hashed_password"] = getHashedPassword(putData["password"])
    putData["userNumber"] = userNumber
    del putData["password"]
    del putData["access_token"]
    del putData["token_type"]
    del putData["refresh_token"]
    value = await updateUserInfo(putData)
    if(value != 0):
        return await getUserInfo(value)
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
        if(str(userNumber) == await decodeToken(deleteData.access_token, deleteData.refresh_token)):
            value = await deleteUserInfo(userNumber)
            if(value == 1):
                return JSONResponse({"result":"success"})
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Delete userInfo failed from DB."
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
    