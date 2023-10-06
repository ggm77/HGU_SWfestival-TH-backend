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
        currentLastNumber = await getLastPostNumber()
        postList = await getLatestPostList_recent(currentLastNumber+1, numberOfPost)
    else:
        postList = await getLatestPostList_recent(targetPostNumber, numberOfPost)

    if(postList):
        return JSONResponse({"postList":postList})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get posting list."
        )


@router.get("/list/recommended")
async def getPostListRecommended(targetPostNumber: Union[int, None] = None, numberOfPost: Union[int, None] = 10):
    return


@router.get("/list/distance")
async def getPostListDistance(targetPostNumber: Union[int, None] = None, numberOfPost: Union[int, None] = 10):
    return

