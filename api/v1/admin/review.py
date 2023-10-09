from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from lib.lib import *
from lib.dto import *
from lib.dto import deletereviewRequest

router = APIRouter(prefix="/api/v1/admin")


@router.post("/disableReview")
async def disableReview(postData: disablereviewRequest):
    tokenDict = await adminVerify(postData.access_token, postData.refresh_token)
    isUpdated = await updateReviewDB({"reviewNumber":postData.reviewNumber, "disabled":True})
    if(isUpdated == -2):
        await raiseDBDownError()
    elif(isUpdated):
        return JSONResponse({"data":{"result":"success"},"token":tokenDict})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disabled review"
        )
    

@router.post("/enableReview")
async def enableReview(postData: enablereviewRequest):
    tokenDict = await adminVerify(postData.access_token, postData.refresh_token)

    isUpdated = await updateReviewDB({"reviewNumber":postData.reviewNumber, "disabled":False})
    if(isUpdated == -2):
        await raiseDBDownError()
    elif(isUpdated):
        return JSONResponse({"data":{"result":"success"},"token":tokenDict})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enabled review"
        )


@router.patch("/review")
async def updateReview(updateData: updatereviewRequest):
    tokenDict = await adminVerify(updateData.access_token, updateData.refresh_token)

    keyList = list(updateData.keys())
    for i in range(len(keyList)):
        if(updateData[keyList[i]] == None):
            del updateData[keyList[i]]
    del updateData["access_token"]
    del updateData["token_type"]
    del updateData["refresh_token"]

    isUpdated = await updateReviewDB(updateData)
    if(isUpdated == -2):
        await raiseDBDownError()
    elif(isUpdated):
        return JSONResponse({"data":{"result":"success"},"token":tokenDict})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update review info."
        )



@router.delete("/review")
async def deleteReview(deleteData: deletereviewRequest):
    tokenDict = await adminVerify(deleteData.access_token, deleteData.refresh_token)

    isDeleted = await deleteReviewDB(deleteData.reviewNumber)
    if(isDeleted == -2):
        await raiseDBDownError()
    if(isDeleted):
        return JSONResponse({"data":{"result":"success"},"token":tokenDict})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete review in DB."
        )


    
