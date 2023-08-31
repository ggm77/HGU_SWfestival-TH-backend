from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from lib.lib import *
from lib.lib import authenticate_user
from lib.schema import *
from lib.schema import tokenRequest, registRequest

router = APIRouter(prefix="/api/v1")




@router.post("/token")
async def token(postData: tokenRequest):
    print(postData.email)
    print(postData.password)

    if(await authenticate_user(postData.email, postData.password)):
        accessToken = await create_access_token(postData.email)
        refreshToken = await create_refresh_token(postData.email)
        result = {"access_token":accessToken, "token_type":"bearer", "refresh_token":refreshToken}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorize error.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return JSONResponse(result)


@router.post("/regist")
async def account(postData: registRequest):
    if(not await checkUserExist(postData.email)):
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