from .DBdataLib import getUserInfo
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext

import json
import os


BASE_DIR = os.path.dirname(os.path.abspath("secrets.json"))
SECRET_FILE = os.path.join(BASE_DIR, "secrets.json")
secrets = json.loads(open(SECRET_FILE).read())

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def authenticate_user(email, password):

    user = await getUserInfo(email)

    if(user == False):
        return False
    
    if(pwd_context.verify(password, user["hashed_password"])):
        return True



async def getAccessToken(username):

    try:
        user = await getUserInfo(username)
    except Exception as e:
        print("[Error]",e,"in",__file__)
        return 

    print("create access token >>", user)
    
    return "ACCESSTOKEN"


def getHashedPassword(password):
    return pwd_context.hash(password)