from fastapi.encoders import jsonable_encoder
from datetime import timedelta, datetime
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

import json

from DB.database import engineconn, rabbitmq
from DB.models import *
from DB.models import userInfo


engine = engineconn()
session = engine.sessionmaker()

rabbitmqClient = rabbitmq()

async def chatSetup(routing_key):
    await rabbitmqClient.setup(routing_key)

async def chatRecodeSetup():
    await rabbitmqClient.setupBackup()

async def createChat(routing_key, body):
    await rabbitmqClient.create_chat(routing_key=routing_key, body=body)

async def backupChat(body):
    await rabbitmqClient.backup_chat(body=body)

async def getChat(routing_key, callback):
    result = await rabbitmqClient.get_chat(routing_key=routing_key, callback=callback)
    return result


async def getLastPostNumber():
    try:
        postNumber = list(session.execute(text('SELECT MAX(postNumber) FROM postInfo')).fetchone())
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return False

    session.close()
    return postNumber[0]

async def getLatestPostList(targetPostNumber, numberOfPost):
    postList = []
    try:
        value = list(session.execute(text(
            f"SELECT JSON_OBJECT(\
                'postNumber',postNumber,\
                'postName', postName,\
                'postUserNumber', postUserNumber,\
                'postDate', postDate,\
                'postType', postType,\
                'postCategory', postCategory,\
                'locationX', locationX,\
                'locationY', locationY,\
                'views', views,\
                'numberOfChat', numberOfChat,\
                'content', content,\
                'disabled', disabled\
                ) FROM postInfo WHERE postNumber < {targetPostNumber} ORDER BY postNumber DESC"
        )))
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return False
    try:
        for i in range(numberOfPost):
            postList.append(json.loads(value[i][0]))
    except IndexError:
        pass
    session.close()
    return postList

async def getNearestPostList(locationX, locationY, distance, numberOfPost):
    postList = []
    try:
        #distance 1 == 1km
        value = list(session.execute(text(
            f"SELECT JSON_OBJECT(\
            'postNumber',postNumber,\
            'postName', postName,\
            'postUserNumber', postUserNumber,\
            'postDate', postDate,\
            'postType', postType,\
            'postCategory', postCategory,\
            'locationX', locationX,\
            'locationY', locationY,\
            'views', views,\
            'numberOfChat', numberOfChat,\
            'content', content,\
            'disabled', disabled\
            ),\
            (6371*acos(cos(radians({locationY}))*cos(radians(locationY))*cos(radians(locationX)-radians({locationX}))\
            +sin(radians({locationY}))*sin(radians(locationY))))AS distance\
            FROM postInfo\
            HAVING distance < 5\
            ORDER BY distance\
            "
        )))
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return False

    try:
        for i in range(numberOfPost):
            postList.append(json.loads(value[i][0]))
    except IndexError:
        pass
    session.close()
    return postList


async def getUserInfo(userNumber):
    try:
        user = jsonable_encoder(session.query(userInfo).get(userNumber))
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
    session.close()
    if(user == None):
        return -1
    elif(user["disabled"] == True):
        return 0
    
    return user

async def getPostInfo(postNumber):
    try:
        post = jsonable_encoder(session.query(postInfo).get(postNumber))
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
    session.close()
    if(post == None):
        return -1
    elif(post["disabled"] == True):
        return 0
    return post

async def getPostPictureList(postNumber):
    try:
        pictureList = (list(session.execute(text(f"SELECT pictureNumber FROM postPicture WHERE postNumber = {postNumber};"))))
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
    except Exception as e:
        print("[DB Error]", e)
        session.close()
        return 0
    session.close()

    result = []
    for i in range(len(pictureList)):
        result.append(pictureList[i][0])

    return result

async def getPostPictureDB(postNumber, pictureNumber):
    
    try:
        file = session.query(postPicture).filter(postPicture.postNumber == postNumber, postPicture.pictureNumber == pictureNumber).first()
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
    except Exception as e:
        print("[DB Error]", e)
        session.close()
        return 0
    session.close()
    return file


async def getUserPictureDB(userNumber):
    try:
        file = session.query(userProfilePicture).filter(userProfilePicture.userNumber == userNumber).first()
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
    except Exception as e:
        print("[DB Error]",e)
        session.close()
        return False
    session.close()
    return file


async def getReviewDB_reviewNumber(reviewNumber):
    try:
        review = jsonable_encoder(session.query(reviewInfo).get(reviewNumber))
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
    session.close()
    if(review == None):
        return -1
    elif(review["disabled"] == True):
        return 0
    else:
        return review


async def getReviewDB_author(authorUserNumber, postNumber):
    try:
        review = session.query(reviewInfo).filter(reviewInfo.authorUserNumber == authorUserNumber, reviewInfo.postNumber == postNumber).first()
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
    except Exception as e:
        print("[DB Error]", e)
        session.close()
        return False
    session.close()
    return review


async def getReviewListDB(userNumber):
    reviewList = []
    try:
        reviewList = list(session.execute(text(f"SELECT reviewNumber FROM reviewInfo WHERE targetUserNumber = {userNumber}")))
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
    except Exception as e:
        print("[DB Error]",e)
        session.close()
        return False
    session.close()
    for i in range(len(reviewList)):
        reviewList[i] = reviewList[i][0]
    return reviewList


async def getChatRoomInfoDB(chatRoomNumber):
    try:
        chatRoomInfo = jsonable_encoder(session.query(chatInfo).get(chatRoomNumber))
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
    except Exception as e:
        print("[DB Error]",e)
        session.close()
        return False
    session.close()
    return chatRoomInfo


async def emailToUserNumber(requestEmail) -> int:
    try:
        result = (session.query(userInfo).filter(userInfo.email == requestEmail).all())[0].userNumber
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
    except IndexError:
        session.close()
        return 0
    session.close()
    return result


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
        rateSum = 0,
        countOfRate = 0,
        disabled = False
    )

    try:
        session.add(data)
        session.commit()
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
    except Exception as e:
        print("[DB Error]", e)
        session.close()
        return False
    session.close()

    userNumber = await emailToUserNumber(user["email"])
    if(userNumber == -2):
        return -2
    info = await getUserInfo(userNumber)
    if(info == -2):
        return -2

    return info


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
        postNumber = list(session.execute(text('SELECT LAST_INSERT_ID() FROM postInfo')).fetchone())
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
    except Exception as e:
        print("[DB Error]", e)
        session.close()
        return False
    session.close()

    info = await getPostInfo(postNumber[0])
    if(info == -2):
        return -2
    return info


async def createPostPicture(file, postNumber, pictureNumber):
    data = postPicture(
        postNumber = postNumber,
        pictureNumber = pictureNumber,
        data = file
    )

    pictureList = await getPostPictureList(postNumber)
    if(pictureList == -2):
        return -2

    if(pictureNumber in pictureList):
        print("[DB Error] pictureNumber already in there.")
        return False

    try:
        session.add(data)
        session.commit()
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
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
    isPictureExist = await getUserPictureDB(userNumber)
    if(isPictureExist == -2):
        return -2
    if(isPictureExist):
        print("[DB Error] userNumber already in DB.")
        return False

    try:
        session.add(data)
        session.commit()
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
    except Exception as e:
        print("[DB Error]", e)
        session.close()
        return False
    session.close()
    return True


async def createReviewDB(reviewData: dict):
    data = reviewInfo(
        authorUserNumber = reviewData["authorUserNumber"],
        targetUserNumber = reviewData["targetUserNumber"],
        reviewDate = datetime.now(),
        rate = reviewData["rate"],
        content = reviewData["content"],
        postNumber = reviewData["postNumber"],
        disabled = False
    )
    try:
        session.add(data)
        session.commit()
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
    except Exception as e:
        print("[DB Error]",e)
        session.close()
        return False
    session.close()

    try:
        reviewNumber = list(session.execute(text("SELECT LAST_INSERT_ID() FROM reviewInfo")).fetchone())
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
    session.close()
    result =  await getReviewDB_reviewNumber(reviewNumber[0])
    if(result == -2):
        return -2
    return result

async def createChatRoomDB(chatRoomData: dict):
    data = chatInfo(
        postNumber = chatRoomData["postNumber"],
        postUserNumber = chatRoomData["postUserNumber"],
        chatterNumber = chatRoomData["userNumber"],
        date = datetime.now()
    )
    try:
        session.add(data)
        session.commit()
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
    except Exception as e:
        print("[DB Error]",e)
        session.close()
        return False
    session.close()

    try:
        chatRoomNumber = list(session.execute(text("SELECT LAST_INSERT_ID() FROM chatInfo")).fetchone())
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
    result = await getChatRoomInfoDB(chatRoomNumber[0])
    if(result == -2):
        return -2
    return result


async def updateUserInfo(user: dict):
    try:
        session.query(userInfo).filter(userInfo.userNumber == user["userNumber"]).update(user)
        session.commit()
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
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
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
    except Exception as e:
        print("[DB Error]", e)
        session.close()
        return 0
    session.close()
    return post["postNumber"]

async def updateReviewDB(review: dict):
    try:
        session.query(reviewInfo).filter(reviewInfo.reviewNumber == review["reviewNumber"]).update(review)
        session.commit()
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
    except Exception as e:
        print("[DB Error]",e)
        session.close()
        return 0
    session.close()
    return review["reviewNumber"]

#not use
async def updateChatRoomInfoDB(chatRoom: dict):
    try:
        session.query(chatInfo).filter(chatInfo.chatRoomNumber == chatRoom["chatRoomNumber"]).update(chatRoom)
        session.commit()
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
    except Exception as e:
        print("[DB Error]",e)
        session.close()
        return False
    session.close()
    return chatRoom["chatRoomNumber"]

async def deleteUserInfo(userNumber: int):
    try:
        session.delete(session.query(userInfo).filter(userInfo.userNumber == userNumber).first())
        session.commit()
        session.close()
        return 1
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
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
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
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
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
    except Exception as e:
        print("[DB Error]", e)
        session.close()
        return False
    
async def deletePostPictureAll(postNumber):
    try:
        session.execute(text(f"DELETE FROM postPicture WHERE postNumber = {str(postNumber)};"))
        session.commit()
        session.close()
        return True
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
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
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
    except Exception as e:
        print("[DB Error]", e)
        session.close()
        return False
    
async def deleteReviewDB(reviewNumber: int):
    try:
        session.delete(session.query(reviewInfo).filter(reviewInfo.reviewNumber == reviewNumber).first())
        session.commit()
        session.close()
        return True
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
    except Exception as e:
        print("[DB Error]", e)
        session.close()
        return False
    

async def deleteChatRoomInfoDB(chatRoomNumber):
    try:
        session.delete(session.query(chatInfo).filter(chatInfo.chatRoomNumber == chatRoomNumber).first())
        session.commit()
        session.close()
        return True
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
    except Exception as e:
        print("[DB Error]",e)
        session.close()
        return False
    
#use not yet
async def deleteChatRecodeDB(chatRoomNumber):
    try:
        session.delete(session.query(chatRecodeInfo).filter(chatRecodeInfo.chatRoomNumber == chatRoomNumber).all())
        session.commit()
        session.close()
        return True
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
    except Exception as e:
        print("[DB Error]",e)
        session.close()
        return False
    

async def viewsPlusOne(postNumber: int):
    try:
        session.execute(text(f"update postInfo set views = postInfo.views + 1 where postNumber = {postNumber};"))
        session.commit()
        session.close()
        return 1
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
    except Exception as e:
        print("[DB Error]", e)
        session.close()
        return 0
    
async def ratePlus(userNumber: int, rate: int):
    try:
        session.execute(text(f"update userInfo set rateSum  = userInfo.rateSum + {rate}, set countOfRate = userInfo.countOfRate + 1 where userNumber = {userNumber}"))
        #session.execute(text(f"update userInfo set countOfRate = userInfo.countOfRate + 1 where userNumber = {userNumber}"))
        session.commit()
        session.close()
        return True
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        return -2
    except Exception as e:
        print("[DB Error]",e)
        session.close()
        return False
    

#not use
# async def rateSubtrack(userNumber: int, rate: int):
#     try:
#         session.execute(text(f"update userInfo set rateSum = userInfo.rateSum - {rate} where userNumber = {userNumber}"))
#         session.execute(text(f"update userInfo set contOfRate = userInfo.countOfRate - 1 where userNumber = {userNumber}"))
#         session.commit()
#         session.close()
#         return True
#     except OperationalError:
#         print(f"[{datetime.now()}] DATABASE DOWN")
#         return -2
#     except Exception as e:
#         print("[DB Error]",e)
#         session.close()
#         return False