from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from lib.lib import *
from lib.dto import *

router = APIRouter(prefix="/api/v1/admin")

@router.post("/disablePost")
async def disablePost(postData: disablepostRequest):
    tokenDict = await adminVerify(postData.access_token, postData.refresh_token)
    param = {"postNumber":postData.targetPostNumber, "disabled":True}
    value = await updatePostInfo(param)
    if(value == -2):
        await raiseDBDownError()
    elif(value != 0):
        return JSONResponse({"data":{"result":"success"},"token":tokenDict})
    else:
        raise HTTPException(
            status_code=status.HTTP_500,
            detail="Failed to update postInfo in DB."
        )


@router.post("/enablePost")
async def enablePost(postData: enablepostRequest):
    tokenDict = await adminVerify(postData.access_token, postData.refresh_token)
    param = {"postNumber":postData.targetPostNumber, "disabled":False}
    value = await updatePostInfo(param)
    if(value == -2):
        await raiseDBDownError()
    elif(value != 0):
        return JSONResponse({"data":{"result":"success"},"token":tokenDict})
    else:
        raise HTTPException(
            status_code=status.HTTP_500,
            detail="Failed to update postInfo in DB."
        )
    

@router.delete("/posting/picture")
async def deletePicture(deleteData: deletepostpicture_adminRequest):
    tokenDict = await adminVerify(deleteData.access_token, deleteData.refresh_token)

    value = await deletePostPicture(deleteData.postNumber, deleteData.pictureNumber)
    if(value == -2):
        await raiseDBDownError()
    elif(value):
        return JSONResponse({"data":{"result":"success"},"token":tokenDict})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete picture from DB."
        )
    

@router.patch("/posting")
async def updatePosting(updateData: updateposting_adminRequest):
    tokenDict = await adminVerify(updateData.access_token, updateData.refresh_token)
    updateData = jsonable_encoder(updateData)

    keyList = list(updateData.keys())
    for i in range(len(keyList)):
        if(updateData[keyList[i]] == None):
            del updateData[keyList[i]]

    del updateData["access_token"]
    del updateData["token_type"]
    del updateData["refresh_token"]

    value = await updatePostInfo(updateData)
    if(value == -2):
        await raiseDBDownError()
    elif(value != 0):
        return JSONResponse({"data":{"result":"success"},"token":tokenDict})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update postInfo in DB."
        )


@router.delete("/posting")
async def deletePosting(deleteData: deleteposting_adminRequest):
    tokenDict = await adminVerify(deleteData.access_token, deleteData.refresh_token)
    value = await deletePostInfo(deleteData.postNumber)
    if(value == -2):
        await raiseDBDownError()
    elif(value == 1):
        isDeleted = await deletePostPictureAll(deleteData.postNumber)
        if(isDeleted == -2):
            await raiseDBDownError()
        elif(not isDeleted):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete picture from DB. (posting deleted)"
            )
        else:
            return JSONResponse({"data":{"result":"success"},"token":tokenDict})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete postInfo in DB."
        )