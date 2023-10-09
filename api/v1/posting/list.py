from fastapi import APIRouter
from fastapi.responses import JSONResponse

from lib.lib import *
from lib.schema import *

router = APIRouter(prefix="/api/v1/posting")


#targetPostNumber 다음 포스트를 보여줌
#show post after targetPostNumber
@router.get("/list/recent")
async def getPostingListRecent(targetPostNumber: Union[int, None] = None, numberOfPost: Union[int, None] = 10):
    
    if(targetPostNumber == None):
        currentLastNumber = int(await getLastPostNumber())
        if(not currentLastNumber):
            await raiseDBDownError()
        postList = await getLatestPostList(currentLastNumber+1, numberOfPost)
    else:
        postList = await getLatestPostList(targetPostNumber, numberOfPost)

    if(postList == False):
        await raiseDBDownError()
    elif(postList[0]):
        return JSONResponse({"postList":postList})
    elif(postList == []):
        return JSONResponse({"postList":None})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get posting list."
        )


@router.get("/list/recommended")
async def getPostListRecommended(locationX: float, locationY: float, distance: Union[int, None] = 0, numberOfPost: Union[int, None] = 10):
    postList = await getNearestPostList(locationX, locationY, distance, numberOfPost)
    if(postList == False):
        await raiseDBDownError()
    elif(postList == []):
        return JSONResponse({"postList":None})
    elif(postList[0]):
        postList.sort(key=lambda x: x["postNumber"])
        return JSONResponse({"postList":postList})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get posting list."
        )


@router.get("/list/distance")
async def getPostListDistance(locationX: float, locationY: float, distance: Union[int, None] = 0, numberOfPost: Union[int, None] = 10):

    # 위도에서 0.008도가 1km
    #https://byul91oh.tistory.com/385

    postList = await getNearestPostList(locationX, locationY, distance, numberOfPost)
    if(postList == False):
        await raiseDBDownError()
    elif(postList == []):
        return JSONResponse({"postList":None})
    elif(postList[0]):
        return JSONResponse({"postList":postList})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get posting list."
        )



