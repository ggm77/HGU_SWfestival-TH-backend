from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from lib.lib import *
from lib.dataClass import *

router = APIRouter(prefix="/api/v1/search")


# mariadb innodb_ft_min_token_size = 2
@router.get("/posting/recent")
async def search(find: str, numberOfPost: int):
    if(len(find) < 2):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The word to find is too short."
        )
    
    find = "* ".join(find.split())
    find += "*"

    result = await searchInDB_recent(find, numberOfPost)
    if(result == -2):
        await raiseDBDownError()
    elif(result):
        return JSONResponse({"data":result})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed search the word."
        )
    

@router.get("/posting/exact")
async def search(find: str, numberOfPost: int):
    if(len(find) < 2):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The word to find is too short."
        )
    
    find = "* ".join(find.split())
    find += "*"

    result = await searchInDB_exact(find, numberOfPost)
    if(result == -2):
        await raiseDBDownError()
    elif(result):
        return JSONResponse({"data":result})
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed search the word."
        )
