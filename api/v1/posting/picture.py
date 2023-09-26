from fastapi import APIRouter, HTTPException, status, UploadFile, Response
from fastapi.responses import JSONResponse

from lib.lib import *
from lib.schema import *

router = APIRouter(prefix="/api/v1/posting")


@router.get("/picture/list")
async def getPictureList(postNumber: int):
    pictureList = await getPostPictureList(postNumber)
    print(pictureList)
    if(pictureList):
        return JSONResponse({"fileList":pictureList})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get picture list from DB."
        )



@router.get("/picture")
async def getPostPicture(postNumber: int, pictureName: int):
    file = await getPostPictureDB(postNumber, pictureName)
    if(file):
        return Response(content=file.data, media_type="image/jpeg")
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File dose not exist."
        )


@router.post("/picture")
async def createPicture(
    file: Union[UploadFile, None],
    postNumber: int,
    pictureNumber: int,
    access_token: str,
    token_type: str,
    refresh_token: str
):
    
    tokenDict = await postUserVerify(access_token, refresh_token, postNumber)

    if(not tokenDict):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Do not have permission."
        )

    if(not file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No upload file sent."
        )
    elif(postNumber == None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No postNumber sent."
        )
    elif(pictureNumber == None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pictureNumber sent."
        )
    else:
        value = await createPostPicture(await file.read(), postNumber, pictureNumber)
        if(value):
            return JSONResponse({"data":{"filename": file.filename},"token":tokenDict})
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload picture to DB."
            )
        

@router.put("/picture")
async def updatePicture(
    file: Union[UploadFile, None],
    postNumber: int,
    pictureNumber: int,
    access_token: str,
    token_type: str,
    refresh_token: str
):
    tokenDict = await postUserVerify(access_token, refresh_token, postNumber)
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
    elif(postNumber == None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No postNumber sent."
        )
    elif(pictureNumber == None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pictureNumber sent."
        )
    else:
        deletevalue = await deletePostPicture(postNumber, pictureNumber)
        if(deletevalue):
            value = await createPostPicture(await file.read(), postNumber, pictureNumber)
            if(value):
                return JSONResponse({"data":{"filename": file.filename},"token":tokenDict})
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
async def deletePicture(deleteData: deletepictureRequest):
    tokenDict = await postUserVerify(deleteData.access_token, deleteData.refresh_token, deleteData.postNumber)
    if(not tokenDict):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Do not have permission"
        )

    if(await deletePostPicture(deleteData.postNumber, deleteData.pictureNumber)):
        return JSONResponse({"data":{"result":"success"},"token":tokenDict})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete picture from DB."
        )