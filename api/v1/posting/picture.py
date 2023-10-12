from fastapi import APIRouter, HTTPException, status, UploadFile, Response
from fastapi.responses import JSONResponse

from lib.lib import *
from lib.dataClass import *

router = APIRouter(prefix="/api/v1/posting")


@router.get("/picture/list")
async def getPictureList(postNumber: int):
    pictureList = await getPostPictureList(postNumber)
    if(pictureList == -2):
        await raiseDBDownError()
    elif(pictureList):
        return JSONResponse({"fileList":pictureList})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get picture list from DB."
        )



# GET - https://hguswfestivalthbackenddb.blob.core.windows.net/post-picture/{postNumber - pictureNumber}.jpeg

# @router.get("/picture")
# async def getPostPicture(postNumber: int, pictureName: int):
#     file = await getPostPictureDB(postNumber, pictureName)
#     if(file == -2):
#         await raiseDBDownError()
#     elif(file):
#         return Response(content=file.data, media_type="image/jpeg")
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="File dose not exist."
#         )


@router.post("/picture")
async def createPicture(
    file: Union[UploadFile, None],
    postNumber: int,
    pictureNumber: int,
    access_token: str,
    token_type: str,
    refresh_token: str
):
    
    if(file.content_type[:5] != "image"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image file allowed."
        )
    
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
        #value = await createPostPicture(await file.read(), postNumber, pictureNumber) #mariadb


        if(file.content_type[6:] != "jpeg"):
            data = await bytesToJpeg(await file.read())
        else:
            data = await file.read()


        
        value = await createPostPicture_azure(data, file.content_type, postNumber, pictureNumber) #azure blob storage
        # if(value == -2):
        #     await raiseDBDownError()
        if(value == -1):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="pictureNumber already in there"
            )
        elif(value):
            return JSONResponse({"data":{"result":"success"},"token":tokenDict})
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
        if(deletevalue == -2):
            await raiseDBDownError()
        elif(deletevalue):
            value = await createPostPicture(await file.read(), postNumber, pictureNumber)
            if(value == -2):
                await raiseDBDownError()
            elif(value):
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

    #isDeleted = await deletePostPicture(deleteData.postNumber, deleteData.pictureNumber)
    isDeleted = await deletePostPicture_azure(deleteData.postNumber, deleteData.pictureNumber)
    if(isDeleted == -2):
        await raiseDBDownError()
    elif(isDeleted):
        return JSONResponse({"data":{"result":"success"},"token":tokenDict})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete picture from DB."
        )