from fastapi import APIRouter, HTTPException, status, UploadFile, Response
from fastapi.responses import JSONResponse, FileResponse

from lib.lib import *
from lib.schema import *

router = APIRouter(prefix="/api/v1/user")


@router.get("/picture")
async def getUserPicture(userNumber: int):
    file = await getUserPictureDB(userNumber)
    if(file):
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

    if(await userNumberVerify(access_token, refresh_token, userNumber)):
        if(await createUserPictureDB(await file.read(), userNumber)):
            return JSONResponse({"result":"success"})
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
    if(not await userNumberVerify(access_token, refresh_token, userNumber)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Do not have permission"
        )

    if(not file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No upload file sent."
        )

    if(await userNumberVerify(access_token, refresh_token, userNumber)):
        if(await deleteUserProfilePicture(userNumber)):
            if(await createUserPictureDB(await file.read(), userNumber)):
                return JSONResponse({"result":"success"})
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
        
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Do not have permission."
        )
    
    

@router.delete("/picture")
async def deleteUserPicture(deleteData: deleteuserpictureRequest):
    if(not await userNumberVerify(deleteData.access_token, deleteData.refresh_token, deleteData.userNumber)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Do not have permission"
        )

    if(await deleteUserProfilePicture(deleteData.userNumber)):
        return JSONResponse({"result":"success"})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete picture from DB."
        )
