from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from lib.lib import authenticate_user, getAccessToken

router = APIRouter(prefix="/api/v1")




class tokenRequest(BaseModel):
    email: str
    password: str

@router.post("/token")
async def token(postData: tokenRequest):
    print(postData.email)
    print(postData.password)

    if(await authenticate_user(postData.email, postData.password)):
        accessToken = await getAccessToken(postData.email)
    else:
        return "authenticate failed"
    return accessToken