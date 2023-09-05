from fastapi import APIRouter
from fastapi.responses import JSONResponse

from lib.lib import *
from lib.schema import *

router = APIRouter(prefix="/api/v1/posting")


@router.get("/list")
async def getPostingList(targetPostNumber: int | None = None):
    
    if(targetPostNumber == None):
        currentLastNumber = await getLastPostNumber()
        postList = await getLatestPostList(currentLastNumber, 10)
    else:
        postList = await getLatestPostList(targetPostNumber, 10)

    return JSONResponse({"postList":postList})