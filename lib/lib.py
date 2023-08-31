from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import timedelta, datetime
from jose import jwt
import json
import os

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



async def authenticate_user(email, password):

    userNumber = await emailToUserNumber(email)

    if(userNumber == False):
        return False
    
    user = await getUserInfo(userNumber)

    if(pwd_context.verify(password, user["hashed_password"])):
        return True
    

async def checkUserExist(userNumber):

    user = await getUserInfo(userNumber)

    if(user):
        return True
    else:
        return False
    

async def registUser(userInfo: dict):

    user = await createUserInfo(userInfo)


    if(user):
        return user
    else:
        return False

async def create_access_token(userNumber):
    data = {"sub":userNumber}
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def create_refresh_token(userNumber):
    data = {"sub":userNumber}
    expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=1)
    to_encode.update({"refresh":"token", "exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def getHashedPassword(password):
    return pwd_context.hash(password)