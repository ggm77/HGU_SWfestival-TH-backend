from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from lib.lib import *
from lib.lib import authenticate_user
from lib.schema import *
from lib.schema import tokenRequest

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
