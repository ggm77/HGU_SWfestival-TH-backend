from fastapi import APIRouter, HTTPException, status, File, UploadFile, Response
from fastapi.responses import JSONResponse, FileResponse
from fastapi.encoders import jsonable_encoder

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


"""
https://fastapi.tiangolo.com/tutorial/request-files/
file request
"""
@router.post("/picture/{postNumber}")#pictureNumber need change!!
async def createPicture(file: UploadFile | None = None, postNumber: str = None, pictureNumber : int = None):
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
        value = await createPostPicture(await file.read(), int(postNumber), pictureNumber)
        if(value):
            return JSONResponse({"filename": file.filename})
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload picture to DB."
            )
    

@router.delete("/picture")
async def deletePicture(deleteData: deletepictureRequest):
    value = await deletePostPicture(deleteData.postNumber, deleteData.pictureNumber)
    if(value):
        return JSONResponse({"result":"success"})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete picture from DB."
        )