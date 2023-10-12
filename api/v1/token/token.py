from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from lib.lib import *
from lib.lib import authenticate_user
from lib.dataClass import *
from lib.dataClass import tokenRequest

router = APIRouter(prefix="/api/v1")


@router.post("/token")
async def token(postData: tokenRequest):
    userNumber = await authenticate_user(postData.email, postData.password)
    
    if(userNumber == -1):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif(userNumber == 0):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password not correct.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif(userNumber):
        accessToken = await create_access_token(userNumber)
        refreshToken = await create_refresh_token(userNumber)
        result = {"access_token":accessToken, "token_type":"bearer", "refresh_token":refreshToken}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorize error.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return JSONResponse(result)
