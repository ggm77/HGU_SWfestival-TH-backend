from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import timedelta, datetime
from jose import jwt, exceptions
import json
import os
from PIL import Image
import io
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
    
    user = await getUserInfo(userNumber)
    if(user == -1):
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
        return 1
    else:
        return 0
    

async def checkUserExist(email) -> bool:
    userNumber = await emailToUserNumber(email)

    if(userNumber):
        return True
    else:
        return False
    

async def registUser(userInfo: dict):

    userInfo["hashed_password"] = getHashedPassword(userInfo["password"])
    del userInfo["password"]

    user = await createUserInfo(userInfo)

    if(user):
        return user
    else:
        return False
    
async def uploadPost(postInfo: dict):

    postInfo["postUserNumber"] = await decodeToken(postInfo["access_token"], postInfo["refresh_token"])
    postInfo["views"] = 0
    postInfo["numberOfChat"] = 0


    del postInfo["access_token"]
    del postInfo["token_type"]
    del postInfo["refresh_token"]

    
    post = await createPostInfo(postInfo)

    if(post):
        return post
    else:
        return False
    
async def uploadReview(data: dict):

    post = await getPostInfo(data["postNumber"])
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
    
    if(post["postUserNumber"] != data["targetUserNumber"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="targetUserNumber not correct."
        )

    data["authorUserNumber"] = await decodeToken(data["access_token"], data["refresh_token"])
    if(str(post["postUserNumber"]) == data["authorUserNumber"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot write review on your own post."
        )

    del data["access_token"]
    del data["token_type"]
    del data["refresh_token"]
    if(await getReviewDB_author(data["authorUserNumber"], data["postNumber"]) == None):
        review = await createReviewDB(data)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="review already in DB."
        )
    if(review):
        if(await ratePlus(data["targetUserNumber"], data["rate"])):
            return review
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="review not counted. (review uploaded)"
        )
    else:
        return False


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
    to_encode.update({"exp": expire})
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
    to_encode.update({"refresh":"token", "exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def decodeToken(token: str, refresh_token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except exceptions.ExpiredSignatureError:
        payload = await decodeRefreshToken(refresh_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload.get("sub")

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
    except Exception as e:
        print("[Token Error]",e)
        return False
    return payload.get("sub")

async def decodeRefreshToken_ws(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception as e:
        print("[Token Error]",e)
        return False
    return payload


async def createChatRoom(data: dict):
    
    value = await createChatRoomDB(data)

    if(value):
        return value
    else:
        return False


async def adminVerify(token: str, refreshToken: str):
    userNumber = await decodeToken(token, refreshToken)
    info = await getUserInfo(userNumber)
    if(info == -1):
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
        return True
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Require admin account."
        )
    
async def postUserVerify(token, refreshToken, postNumber):
    postUserNumber = (await getPostInfo(postNumber))["postUserNumber"]
    tokenUserNumber = await decodeToken(token, refreshToken)
    if(str(postUserNumber) == tokenUserNumber):
        return True
    else:
        return False
    
async def userNumberVerify(token, refreshToken, userNumber):
    tokenUserNumber = await decodeToken(token, refreshToken)
    if(str(userNumber) == tokenUserNumber):
        return True
    else:
        return False
    

def getHashedPassword(password):
    return pwd_context.hash(password)
