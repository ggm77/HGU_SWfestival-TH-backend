from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import timedelta, datetime
from jose import jwt, exceptions
import json
import os
from PIL import Image
import io
from io import BytesIO
import time

from lib.DBdataLib import *

BASE_DIR = os.path.dirname(os.path.abspath("secrets.json"))
SECRET_FILE = os.path.join(BASE_DIR, "secrets.json")
secrets = json.loads(open(SECRET_FILE).read())

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = secrets["server"]["SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 1

async def create_access_token(target):
    if(type(target) != str):
        target = str(target)
    data = {"sub":target}
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"type":"access","exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def create_refresh_token(target):
    if(type(target) != str):
        target = str(target)
    data = {"sub":target}
    expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=1)
    to_encode.update({"type":"refresh", "exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def create_token(target):
    return {"access_token":await create_access_token(target),"refresh_token":await create_refresh_token(target)}

async def decodeToken(token: str, refresh_token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except exceptions.ExpiredSignatureError:
        payload = await decodeRefreshToken(refresh_token)
        if(payload == False):
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

async def decodeRefreshToken(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    return payload


async def decodeToken_ws(token: str, refresh_token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except exceptions.ExpiredSignatureError:
        payload = await decodeRefreshToken_ws(refresh_token)
        if(payload == False):
            return False
    except Exception as e:
        print("[Token Error]",e)
        return False
    return payload

async def decodeRefreshToken_ws(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception as e:
        print("[Token Error]",e)
        return False
    return payload


async def getDefaultProfilePicture():
    path = os.path.dirname(os.path.abspath(__file__))[:-3]
    path += "assets/defaultProfileImage/defaultProfile.png"
    img = Image.open(path, mode='r')

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


async def passwordVerify(plain, hashed):
    return pwd_context.verify(plain, hashed)


async def authenticate_user(email, password):

    userNumber = await emailToUserNumber(email)
    if(userNumber == 0):
        return -1
    elif(userNumber == -2):
        await raiseDBDownError()
    
    user = await getUserInfo(userNumber)
    if(user == -2):
        await raiseDBDownError()
    elif(user == -1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found."
        )
    elif(user == 0):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User disabled"
        )

    if(await passwordVerify(password, user["hashed_password"])):
        return userNumber
    else:
        return 0
    

async def checkUserExist(email)->bool:
    userNumber = await emailToUserNumber(email)

    if(userNumber):
        return True
    else:
        return False
    

async def registUser(userInfo: dict):

    userInfo["hashed_password"] = getHashedPassword(userInfo["password"])
    del userInfo["password"]

    user = await createUserInfo(userInfo)

    if(user == -2):
        await raiseDBDownError()
    if(user):
        return user
    else:
        return False
    
async def uploadPost(postInfo: dict):
    payload = await decodeToken(postInfo["access_token"], postInfo["refresh_token"])
    postInfo["postUserNumber"] = payload.get("sub")
    postInfo["views"] = 0
    postInfo["numberOfChat"] = 0

    
    post = await createPostInfo(postInfo)

    if(post == -2):
        await raiseDBDownError()
    elif(post):
        if(payload.get("type")=="refresh"):
            return {"data":post,"token":await create_token(payload.get("sub"))}
        else:
            return {"data":post,"token":{"access_token":postInfo["access_token"],"refresh_token":postInfo["refresh_token"]}}
    else:
        return False
    
async def uploadReview(data: dict):

    #post = await getPostInfo(data["postNumber"])
    post = await getChatRoomInfoDB(data["chatRoomNumber"])
    if(post == -2):
        await raiseDBDownError()
    elif(post == False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chat room not found."
        )
    
    if(post["postUserNumber"] != data["targetUserNumber"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="targetUserNumber not correct."
        )
    payload = await decodeToken(data["access_token"], data["refresh_token"])
    data["authorUserNumber"] = payload.get("sub")
    if(str(post["postUserNumber"]) == data["authorUserNumber"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot write review on your own post."
        )
    elif(str(post["chatterNumber"]) != data["authorUserNumber"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You cannot write review."
        )


    author = await getReviewDB_author(data["authorUserNumber"], data["chatRoomNumber"])
    if(author == -2):
        await raiseDBDownError()
    elif(author == None):
        review = await createReviewDB(data)
        if(review == -2):
            await raiseDBDownError()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="review already in DB."
        )
    if(review):
        isAdded = await ratePlus(data["targetUserNumber"], data["rate"])
        if(isAdded == -2):
            await raiseDBDownError()
        elif(isAdded):
            if(payload.get("type")=="refresh"):
                return {"data":review,"token":await create_token(payload.get("sub"))}
            else:
                return {"data":review,"token":{"access_token":data["access_token"],"refresh_token":data["refresh_token"]}}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="review not counted. (review uploaded)"
        )
    else:
        return False




async def createChatRoom(data: dict):
    
    value = await createChatRoomDB(data)

    if(value == -2):
        await raiseDBDownError()
    elif(value):
        return value
    else:
        return False
    


async def adminVerify(token: str, refreshToken: str):
    payload = await decodeToken(token, refreshToken)
    userNumber = payload.get("sub")
    info = await getUserInfo(userNumber)
    if(info == -2):
        await raiseDBDownError()
    elif(info == -1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found."
        )
    elif(info == 0):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User disabled"
        )
    if(info["userType"] == "admin"):
        if(payload.get("type") == "refresh"):
            return {"access_token":await create_access_token(userNumber),"refresh_token":await create_refresh_token(userNumber)}
        else:
            return {"access_token":token,"refresh_token":refreshToken}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Require admin account."
        )
    
async def postUserVerify(token, refreshToken, postNumber):
    info = await getPostInfo(postNumber)
    if(info == -2):
        await raiseDBDownError()
    elif(info == -1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post not found."
        )
    elif(info == 0):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Post disabled."
        )
    postUserNumber = (await getPostInfo(postNumber))["postUserNumber"]
    payload = await decodeToken(token, refreshToken)
    tokenUserNumber = payload.get("sub")
    if(str(postUserNumber) == tokenUserNumber):
        if(payload.get("type")=="refresh"):
            return await create_token(tokenUserNumber)
        else:
            return {"access_token":token,"refresh_token":refreshToken}
    else:
        return False
    
async def userNumberVerify(token, refreshToken, userNumber):
    payload = await decodeToken(token, refreshToken)
    tokenUserNumber = payload.get("sub")
    if(str(userNumber) == tokenUserNumber):
        if(payload.get("type")=="refresh"):
            return await create_token(payload.get("sub"))
        else:
            return {"access_token":token,"refresh_token":refreshToken}
    else:
        return False


async def raiseDBDownError():
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="DATABASE DOWN"
    )

async def bytesToJpeg(data):
    buffer = io.BytesIO()
    image = Image.open(BytesIO(data)).convert("RGB")
    image.save(buffer, format="jpeg")
    return buffer.getvalue()

def getHashedPassword(password):
    return pwd_context.hash(password)
