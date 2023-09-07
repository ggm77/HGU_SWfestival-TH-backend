from fastapi.encoders import jsonable_encoder
from datetime import timedelta, datetime
from sqlalchemy import text

from DB.database import engineconn
from DB.models import *
from DB.models import userInfo

"""

what if % or \ in there?

"""

engine = engineconn()
session = engine.sessionmaker()


async def getLastPostNumber():
    postNumber = list(session.execute(text('SELECT MAX(postNumber) FROM postInfo')).fetchone())
    session.close()
    return postNumber[0]

async def getLatestPostList(targetPostNumber, numberOfPost):
    #Return including number targetPostNumber
    postList = []
    targetPostNumber += 1
    for i in range(numberOfPost):
        if(targetPostNumber != 1):
            value = int(list(session.execute(text(f"SELECT MAX(postNumber) FROM postInfo WHERE postNumber < {targetPostNumber}")))[0][0])
            postList.append(value)
            targetPostNumber = value
        else:
            break
    session.close()
    return postList


async def getUserInfo(userNumber):

    user = jsonable_encoder(session.query(userInfo).get(userNumber))
    session.close()
    if(user == None):
        return -1
    elif(user["disabled"] == True):
        return 0
    
    return user

async def getPostInfo(postNumber):

    post = jsonable_encoder(session.query(postInfo).get(postNumber))
    session.close()
    if(post == None):
        return -1
    elif(post["disabled"] == True):
        return 0
    return post

async def getPostPictureList(postNumber):
    try:
        pictureList = (list(session.execute(text(f"SELECT pictureNumber FROM postPicture WHERE postNumber = {postNumber};"))))
    except Exception as e:
        print("[DB Error]", e)
        session.close()
        return False
    session.close()

    result = []
    for i in range(len(pictureList)):
        result.append(pictureList[i][0])

    return result

async def getPostPictureDB(postNumber, pictureNumber):
    
    try:
        file = session.query(postPicture).filter(postPicture.postNumber == postNumber, postPicture.pictureNumber == pictureNumber).first()
    except Exception as e:
        print("[DB Error]", e)
        session.close()
        return False
    session.close()
    return file


async def getUserPictureDB(userNumber):
    try:
        file = session.query(userProfilePicture).filter(userProfilePicture.userNumber == userNumber).first()
    except Exception as e:
        print("[DB Error]",e)
        session.close()
        return False
    session.close()
    return file



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

    try:
        session.add(data)
        session.commit()
    except Exception as e:
        print("[DB Error]", e)
        session.close()
        return False
    session.close()

    return await getUserInfo(await emailToUserNumber(user["email"]))

async def createPostInfo(post: dict):
    data = postInfo(
        postName = post["postName"],
        postUserNumber = post["postUserNumber"],
        postDate = datetime.now(),
        postType = post["postType"],
        postCategory = post["postCategory"],
        locationX = post["locationX"],
        locationY = post["locationY"],
        views = 0,
        numberOfChat = 0,
        content = post["content"],
        disabled = False
    )

    try:
        session.add(data)
        session.commit()
        postNumber = list(session.execute(text('SELECT LAST_INSERT_ID() AS id')).fetchone())
    except Exception as e:
        print("[DB Error]", e)
        session.close()
        return False
    session.close()

    return await getPostInfo(postNumber[0])


async def createPostPicture(file, postNumber, pictureNumber):
    data = postPicture(
        postNumber = postNumber,
        pictureNumber = pictureNumber,
        data = file
    )

    if(pictureNumber in await getPostPictureList(postNumber)):
        print("[DB Error] pictureNumber already in there.")
        return False

    try:
        session.add(data)
        session.commit()
    except Exception as e:
        print("[DB Error]", e)
        session.close()
        return False
    session.close()
    return True


async def createUserPictureDB(file, userNumber):
    data = userProfilePicture(
        userNumber = userNumber,
        data = file
    )

    if(await getUserPictureDB(userNumber)):
        print("[DB Error] userNumber already in DB.")
        return False

    try:
        session.add(data)
        session.commit()
    except Exception as e:
        print("[DB Error]", e)
        session.close()
        return False
    session.close()
    return True


async def emailToUserNumber(requestEmail) -> int:
    try:
        result = (session.query(userInfo).filter(userInfo.email == requestEmail).all())[0].userNumber
    except IndexError:
        session.close()
        return 0
    session.close()
    return result


async def updateUserInfo(user: dict):
    try:
        session.query(userInfo).filter(userInfo.userNumber == user["userNumber"]).update(user)
        session.commit()
    except Exception as e:
        print("[DB Error]", e)
        session.close()
        return 0
    session.close()
    return user["userNumber"]


async def updatePostInfo(post: dict):
    try:
        session.query(postInfo).filter(postInfo.postNumber == post["postNumber"]).update(post)
        session.commit()
    except Exception as e:
        print("[DB Error]", e)
        session.close()
        return 0
    session.close()
    return post["postNumber"]


async def deleteUserInfo(userNumber: int):
    try:
        session.delete(session.query(userInfo).filter(userInfo.userNumber == userNumber).first())
        session.commit()
        session.close()
        return 1
    except Exception as e:
        print("[DB Error]", e)
        session.close()
        return 0
    
async def deletePostInfo(postNumber: int):
    try:
        session.delete(session.query(postInfo).filter(postInfo.postNumber == postNumber).first())
        session.commit()
        session.close()
        return 1
    except Exception as e:
        print("[DB Error]", e)
        session.close()
        return 0
    
async def deletePostPicture(postNumber, pictureNumber):
    try:
        session.delete(session.query(postPicture).filter(postPicture.postNumber == postNumber, postPicture.pictureNumber == pictureNumber).first())
        session.commit()
        session.close()
        return True
    except Exception as e:
        print("[DB Error]", e)
        session.close()
        return False
    
async def deleteUserProfilePicture(userNumber):
    try:
        session.delete(session.query(userProfilePicture).filter(userProfilePicture.userNumber == userNumber).first())
        session.commit()
        session.close()
        return True
    except Exception as e:
        print("[DB Error]", e)
        session.close()
        return False
    
async def viewsPlusOne(postNumber: int):
    try:
        session.execute(text(f"update postInfo set views = postInfo.views + 1 where postNumber = {postNumber};"))
        session.commit()
        session.close()
        return 1
    except Exception as e:
        print("[DB Error]", e)
        session.close()
        return 0