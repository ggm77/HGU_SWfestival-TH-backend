from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from lib.lib import *
from lib.schema import *

router = APIRouter(prefix="/api/v1")

@router.post("/verification")
async def verificationPassword(postData: verificationRequest):
    payload = await decodeToken(postData.access_token, postData.refresh_token)
    userNumber = payload.get("sub")
    info = await getUserInfo(userNumber)
    if(await passwordVerify(postData.password, info["hashed_password"])):
        if(payload.get("type")=="refresh"):
            return JSONResponse({"data":{"result":"success"},"token":await create_token(payload.get("sub"))})
        else:
            return JSONResponse({"data":{"result":"success"},"token":{"access_token":postData.access_token,"refresh_token":postData.refresh_token}})
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password verfiy error."
        )
