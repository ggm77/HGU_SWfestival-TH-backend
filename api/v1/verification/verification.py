from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from lib.lib import *
from lib.schema import *

router = APIRouter(prefix="/api/v1")

@router.post("/verification")
async def verificationPassword(postData: verificationRequest):
    userNumber = await decodeToken(postData.access_token, postData.refresh_token)
    info = await getUserInfo(userNumber)
    if(await passwordVerify(postData.password, info["hashed_password"])):
        return JSONResponse({"verify":"success"})
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password verfiy error."
        )
