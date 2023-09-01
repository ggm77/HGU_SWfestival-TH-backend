from fastapi.encoders import jsonable_encoder
from datetime import timedelta, datetime

from DB.database import engineconn
from DB.models import *
from DB.models import userInfo



engine = engineconn()
session = engine.sessionmaker()


async def getUserInfo(userNumber):
    #if nothing in there?

    user = jsonable_encoder(session.query(userInfo).get(userNumber))
    session.close()
    if(user["disabled"] == True):
        return False
    
    return user

async def createUserInfo(user: dict):
    data = userInfo(
        username = user["username"],
        hashed_password = user["hashed_password"],
        userType = "user",
        signUpDate = datetime.now(),
        email = user["email"],
        locationX = user["locationX"],
        locationY = user["locationY"],
        point = 0,
        disabled = False
    )

    session.add(data)
    session.commit()
    session.close()

    return await getUserInfo(await emailToUserNumber(user["email"]))


async def emailToUserNumber(requestEmail) -> int:
    try:
        result = (session.query(userInfo).filter(userInfo.email == requestEmail).all())[0].userNumber
    except IndexError:
        session.close()
        return 0
    session.close()
    return result


async def updateUserInfo(user: dict):
    #not complete
    try:
        session.add(session.query(userInfo).filter())
    except:
        return


async def deleteUserInfo(userNumber):
    try:
        session.delete(session.query(userInfo).filter(userInfo.userNumber == userNumber).first())
        session.commit()
        session.close()
        return 1
    except Exception as e:
        print(e)
        session.close()
        return 0