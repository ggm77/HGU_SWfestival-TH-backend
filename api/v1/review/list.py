from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from lib.lib import *
from lib.dataClass import *

router = APIRouter(prefix="/api/v1/review")

@router.get("/list/{userNumber}")
async def getReviewList(userNumber: int):
    review = await getReviewListDB(userNumber)
    if(review == -2):
        await raiseDBDownError()
    elif(review):
        return JSONResponse({"reviewList":review})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get review list."
        )
