from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from lib.lib import *
from lib.schema import *

router = APIRouter(prefix="/api/v1")


@router.post("/posting")
async def createPosting(postData: createpostingRequest):
    info = jsonable_encoder(postData)

    post = await uploadPost(info)

    if(post):
        return JSONResponse(post)
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register posting."
        )
    

@router.get("/posting")
async def getPosting(postNumber: int, access_token: str | None = None, token_type: str | None = None, refresh_token: str | None = None):
    if(access_token != None and refresh_token != None):
        try:
            await decodeToken(access_token, refresh_token)
        except:
            print("Access token error.")
            pass
        if(await viewsPlusOne(postNumber) == 0):
                print("Views did not increase.")
                pass
        

    value = await getPostInfo(postNumber)
    if(value == -1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post not found."
        )
    elif(value == 0):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Post disabled."
        )

    return JSONResponse(value)

@router.patch("/posting")
async def updatePosting(updateData: updatepostingRequest):
    userNumber = await decodeToken(updateData.access_token, updateData.refresh_token)
    post = await getPostInfo(updateData.postNumber)

    if(post == -1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post not found."
        )
    elif(post == 0):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Post disabled."
        )


    if(str(post["postUserNumber"]) == userNumber):
        data = jsonable_encoder(updateData)

        del data["access_token"]
        del data["token_type"]
        del data["refresh_token"]

        value = await updatePostInfo(data)
        if(value != 0):
            return await getPostInfo(value)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update posting in DB."
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorize user."
        )

    


@router.delete("/posting")
async def deletePosting(deleteData: deletepostingRequest):
    userNumber = await decodeToken(deleteData.access_token, deleteData.refresh_token)
    post = await getPostInfo(deleteData.postNumber)

    if(post == -1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post not found."
        )
    elif(post == 0):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Post disabled"
        )


    if(str(post["postUserNumber"]) == userNumber):
        value = await deletePostInfo(deleteData.postNumber)
        if(not await deletePostPicture(deleteData.postNumber, deleteData.pictureNumber)):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete picture from DB."
            )
        if(value == 1):
            return JSONResponse({"result":"success"})
        else:
            raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failded to delete posting in DB."
                )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="UserInfo is incorrect"
        )
    
