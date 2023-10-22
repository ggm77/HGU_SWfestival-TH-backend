from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from lib.lib import *
from lib.dataClass import *

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

    isDeleted = await deletePostPicture_azure(deleteData.postNumber, deleteData.pictureNumber)
    if(isDeleted == -1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File does not exist."
        )
    elif(isDeleted):
        isDeletedInDB = await deletePostPictureURL_DB(deleteData.postNumber, deleteData.pictureNumber)
        if(isDeletedInDB == -2):
            await raiseDBDownError()
        elif(isDeletedInDB):
            return JSONResponse({"data":{"result":"success"},"token":tokenDict})
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete picture from DB.(File deleted in AZURE)"
            )
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
        isDeletedAzure = await deletePostPictureAll_azure(deleteData.postNumber)
        if(isDeletedAzure == -1):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Picture not exist in azure blob."
            )
        elif(isDeletedAzure != True):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete picture in azure blob."
            )

        isDeletedDB = await deletePostPictureAll_DB(deleteData.postNumber)
        if(isDeletedDB == -2):
            await raiseDBDownError()
        elif(not isDeletedDB):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete picture from DB. (posting deleted, azure blob deleted)"
            )
        else:
            return JSONResponse({"data":{"result":"success"},"token":tokenDict})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete postInfo in DB."
        )