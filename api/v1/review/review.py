from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from lib.lib import *
from lib.schema import *

router = APIRouter(prefix="/api/v1")

@router.post("/review")
async def createReview(postData: createreviewRequest):
    postData = jsonable_encoder(postData)
    
    value = await uploadReview(postData)

    if(value):
        return JSONResponse(value)
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create review to DB."
        )
    

@router.get("/review/{reviewNumber}")
async def getReview(reviewNumber: int):
    review = await getReviewDB_reviewNumber(reviewNumber)
    if(review == -2):
        await raiseDBDownError()
    elif(review == -1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review not found."
        )
    elif(review == 0):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Review disabled."
        )
    else:
        return JSONResponse(review)