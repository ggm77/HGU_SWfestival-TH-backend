from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from lib.lib import *
from lib.dataClass import *

router = APIRouter(prefix="/api/v1")


@router.post("/posting")
async def createPosting(postData: createpostingRequest):
    if(postData.postType != "lost" and postData.postType != "found"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="lostType is not correct."
        )

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
async def getPosting(postNumber: int, access_token: Union[str, None] = None, token_type: Union[str, None] = None, refresh_token: Union[str, None] = None):
    if(access_token != None and refresh_token != None):
        try:
            payload = await decodeToken(access_token, refresh_token)
        except:
            print("Access token error.")
            pass
        isAdded = await viewsPlusOne(postNumber)
        if(isAdded == -2):
            await raiseDBDownError()
        elif(isAdded == 0):
                print("Views did not increase.")
                pass
        

    value = await getPostInfo(postNumber)
    if(value == -2):
        await raiseDBDownError()
    elif(value == -1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post not found."
        )
    elif(value == 0):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Post disabled."
        )
    


    if(access_token != None and refresh_token != None):
        if(payload.get("type")=="refresh"):
            return JSONResponse({"data":value,"token":await create_token(payload.get("sub"))})
        else:
            return JSONResponse({"data":value,"token":{"access_token":access_token,"refresh_token":refresh_token}})
    else:
        return JSONResponse({"data":value,"token":None})

@router.patch("/posting")
async def updatePosting(updateData: updatepostingRequest):
    payload = await decodeToken(updateData.access_token, updateData.refresh_token)
    userNumber = payload.get("sub")
    post = await getPostInfo(updateData.postNumber)
    if(post == -2):
        await raiseDBDownError()
    elif(post == -1):
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

        keyList = list(data.keys())
        for i in range(len(keyList)):
            if(data[keyList[i]] == None):
                del data[keyList[i]]

        del data["access_token"]
        del data["token_type"]
        del data["refresh_token"]

        value = await updatePostInfo(data)
        if(value == -2):
            await raiseDBDownError()
        post = await getPostInfo(value)
        if(post == -2):
            await raiseDBDownError()

        if(value != 0):
            if(payload.get("type")=="refresh"):
                return JSONResponse({"data":post,"token":await create_token(payload.get("sub"))})
            else:
                return JSONResponse({"data":post,"token":{"access_token":updateData.access_token,"refresh_token":updateData.refresh_token}})
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
    payload = await decodeToken(deleteData.access_token, deleteData.refresh_token)
    userNumber = payload.get("sub")
    post = await getPostInfo(deleteData.postNumber)

    if(post==-2):
        await raiseDBDownError()
    elif(post == -1):
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
        if(value == -2):
            await raiseDBDownError()
        if(value == 1):
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
                return JSONResponse({"data":{"result":"success"},"token":await create_token(payload.get("sub"))})
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
    
