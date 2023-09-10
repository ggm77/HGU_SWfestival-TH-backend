from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from lib.lib import *
from lib.schema import *
from lib.schema import deletereviewRequest

router = APIRouter(prefix="/api/v1/admin")


@router.post("/disableReview")
async def disableReview(postData: disablereviewRequest):
    await adminVerify(postData.access_token, postData.refresh_token)

    if(await updateReviewDB({"reviewNumber":postData.reviewNumber, "disabled":True})):
        return JSONResponse({"result":"success"})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disabled review"
        )
    

@router.post("/enableReview")
async def enableReview(postData: enablereviewRequest):
    await adminVerify(postData.access_token, postData.refresh_token)

    if(await updateReviewDB({"reviewNumber":postData.reviewNumber, "disabled":False})):
        return JSONResponse({"result":"success"})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enabled review"
        )


@router.patch("/review")
async def updateReview(updateData: updatereviewRequest):
    await adminVerify(updateData.access_token, updateData.refresh_token)

    keyList = list(updateData.keys())
    for i in range(len(keyList)):
        if(updateData[keyList[i]] == None):
            del updateData[keyList[i]]
    del updateData["access_token"]
    del updateData["token_type"]
    del updateData["refresh_token"]

    if(await updateReviewDB(updateData)):
        return JSONResponse({"result":"success"})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update review info."
        )



@router.delete("/review")
async def deleteReview(deleteData: deletereviewRequest):
    await adminVerify(deleteData.access_token, deleteData.refresh_token)

    if(await deleteReviewDB(deleteData.reviewNumber)):
        return JSONResponse({"result":"success"})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete review in DB."
        )


    
