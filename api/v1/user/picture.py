from fastapi import APIRouter, HTTPException, status, UploadFile, Response
from fastapi.responses import JSONResponse, FileResponse

from lib.lib import *
from lib.dto import *

router = APIRouter(prefix="/api/v1/user")


@router.get("/picture")
async def getUserPicture(userNumber: int):
    file = await getUserPictureDB(userNumber)
    if(file == -2):
        await raiseDBDownError()
    elif(file):
        result = file.data
    else:
        result = await getDefaultProfilePicture()
    return Response(content=result, media_type="image/jpeg")


@router.post("/picture")
async def createUserPicture(
    file : Union[UploadFile, None],
    userNumber : int,
    access_token: str,
    token_type: str,
    refresh_token: str
):
    if(not file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No upload file sent."
        )
    tokenDict = await userNumberVerify(access_token, refresh_token, userNumber)
    if(tokenDict):
        isCreatedPicture = await createUserPictureDB(await file.read(), userNumber)
        if(isCreatedPicture == -2):
            await raiseDBDownError()
        elif(isCreatedPicture):
            return JSONResponse({"data":{"result":"success"},"token":tokenDict})
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload picture to DB."
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Do not have permission."
        )
    

@router.put("/picture")
async def updateUserPicture(
    file : Union[UploadFile, None],
    userNumber : int,
    access_token: str,
    token_type: str,
    refresh_token: str
):
    tokenDict = await userNumberVerify(access_token, refresh_token, userNumber)
    if(not tokenDict):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Do not have permission"
        )

    if(not file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No upload file sent."
        )
    isDeleted = await deleteUserProfilePicture(userNumber)
    if(isDeleted == -2):
        await raiseDBDownError()
    elif(isDeleted):
        isCreatedPicture = await createUserPictureDB(await file.read(), userNumber)
        if(isCreatedPicture == -2):
            await raiseDBDownError()
        if(isCreatedPicture):
            return JSONResponse({"data":{"result":"success"},"token":tokenDict})
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload picture to DB."
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete picture from DB."
        )

    

@router.delete("/picture")
async def deleteUserPicture(deleteData: deleteuserpictureRequest):
    tokenDict = await userNumberVerify(deleteData.access_token, deleteData.refresh_token, deleteData.userNumber)
    if(not tokenDict):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Do not have permission"
        )
    isDeleted = await deleteUserProfilePicture(deleteData.userNumber)
    if(isDeleted == -2):
        await raiseDBDownError()
    elif(isDeleted):
        return JSONResponse({"data":{"result":"success"},"token":tokenDict})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete picture from DB."
        )
