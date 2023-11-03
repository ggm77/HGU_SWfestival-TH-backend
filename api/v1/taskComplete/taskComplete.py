from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from lib.lib import *
from lib.dataClass import *

router = APIRouter(prefix="/api/v1")

@router.post("/taskComplete")
async def taskComplete(postData: taskcompleteRequest):
    token = await userNumberVerify(postData.access_token, postData.refresh_token, postData.userNumber)

    posting = await getPostInfo(postData.postNumber)

    if(posting == 0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Posting already completed."
        )
    elif(posting == -1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Posting not found."
        )
    elif(posting == -2):
        await raiseDBDownError()
    elif(posting):
        isCompleted = await postingTaskComplete(postData.postNumber, postData.foundUserNumber)
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change state."
        )


    if(isCompleted):
        return JSONResponse({"result":"success","token":token})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change state."
        )
