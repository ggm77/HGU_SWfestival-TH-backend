from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from lib.lib import *
from lib.lib import authenticate_user
from lib.schema import *
from lib.schema import tokenRequest, registRequest

router = APIRouter(prefix="/api/v1")




@router.post("/token")
async def token(postData: tokenRequest):
    authUser = await authenticate_user(postData.email, postData.password)
    if(authUser == 1):
        userNumber = await emailToUserNumber(postData.email)
        accessToken = await create_access_token(userNumber)
        refreshToken = await create_refresh_token(userNumber)
        result = {"access_token":accessToken, "token_type":"bearer", "refresh_token":refreshToken}
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
    return JSONResponse(result)

@router.post("/verification")
async def verification(postData: verificationRequest):
    userNumber = await decodeToken(postData.access_token)
    if(passwordVerify(postData.password, await getUserInfo(userNumber)["hashed_password"])):
        return JSONResponse({"verify":"success"})
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password verfiy error."
        )


@router.post("/regist")
async def account(postData: registRequest):

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
    

@router.post("/userinfo")
async def userinfo(postData: userinfoRequest):
    userNumber = await decodeToken(postData.access_token)
    user = await getUserInfo(userNumber)
    if(not user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not found or user disabled."
        )
    del user["hashed_password"]

    return JSONResponse(jsonable_encoder(user))
    

@router.post("/updateuser")
async def updateUser(postData: updateuserRequest):
    value = await updateUserInfo(jsonable_encoder())
    return


@router.post("/deleteuser")
async def deleteUser(postData: deleteuserRequest):
    authUser = await authenticate_user(postData.email, postData.password)
    if(authUser == 1):
        userNumber = await emailToUserNumber(postData.email)
        if(str(userNumber) == await decodeToken(postData.access_token)):
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
    





@router.post("/test")
async def testPage():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %X")