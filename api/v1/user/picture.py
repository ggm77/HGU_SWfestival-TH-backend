from fastapi import APIRouter, HTTPException, status, UploadFile, Response
from fastapi.responses import JSONResponse, FileResponse

from lib.lib import *
from lib.dataClass import *

router = APIRouter(prefix="/api/v1/user")


@router.get("/picture")
async def getUserPicture(userNumber: int):
    url = await getUserPictureDB(userNumber)
    if(url == -2):
        await raiseDBDownError()
    elif(url):
        # result = file.data
        return JSONResponse({"url":url})
    else:
        # result = await getDefaultProfilePicture()
        return JSONResponse({"url":"https://hguswfestivalthbackenddb.blob.core.windows.net/user-profile-picture/defaultProfile.jpeg"})
    # return Response(content=result, media_type="image/jpeg")


@router.post("/picture")
async def createUserPicture(
    file : Union[UploadFile, None],
    userNumber : int,
    access_token: str,
    token_type: str,
    refresh_token: str
):
    
    if(file.content_type[:5] != "image"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image file allowed."
        )
    
    if(not file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No upload file sent."
        )
    tokenDict = await userNumberVerify(access_token, refresh_token, userNumber)
    if(tokenDict):

        if(file.content_type[6:] != "jpeg"):
            data = await bytesToJpeg(await file.read())
        else:
            data = await file.read()


        imageURL = await createUserPicture_azure(data, userNumber)

        if(imageURL == -1):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User profile picture already exist in azure."
            )

        # isCreatedPicture = await createUserPictureDB(await file.read(), userNumber)
        isCreatedPicture = await createUserPictureURL_DB(imageURL, userNumber)
        if(isCreatedPicture == -1):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User profile picture already exist in DB. (uploaded in azure.)"
            )
        elif(isCreatedPicture == -2):
            await raiseDBDownError()
        elif(isCreatedPicture):
            return JSONResponse({"data":{"url":imageURL},"token":tokenDict})
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload picture to DB.(uploaded in azure.)"
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
    
    if(file.content_type[:5] != "image"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image file allowed."
        )

    if(not file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No upload file sent."
        )


    isDeletedAzure = await deleteUserProfilePicture_azure(userNumber)

    if(isDeletedAzure == -1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User profile picture not exist in azure."
        )
    elif(isDeletedAzure == False):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user profile picture in azure."
        )

    if(file.content_type[6:] != "jpeg"):
        data = await bytesToJpeg(await file.read())
    else:
        data = await file.read()
    imageURL = await createUserPicture_azure(data, userNumber)

    if(imageURL == -1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User profile picture already exist in azure."
        )

    return JSONResponse({"data":{"url":imageURL},"token":tokenDict})



    

@router.delete("/picture")
async def deleteUserPicture(deleteData: deleteuserpictureRequest):
    tokenDict = await userNumberVerify(deleteData.access_token, deleteData.refresh_token, deleteData.userNumber)
    if(not tokenDict):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Do not have permission"
        )
    isDeletedAzure = await deleteUserProfilePicture_azure(deleteData.userNumber)

    if(isDeletedAzure == -1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User profile picture not exist in azure."
        )
    elif(isDeletedAzure == False):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user profile picture in azure."
        )

    isDeleted = await deleteUserProfilePictureURL_DB(deleteData.userNumber)
    if(isDeleted == -2):
        await raiseDBDownError()
    elif(isDeleted):
        return JSONResponse({"data":{"result":"success"},"token":tokenDict})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete url from DB (picture deleted in azure)."
        )
