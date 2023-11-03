from fastapi.encoders import jsonable_encoder
from datetime import timedelta, datetime
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

import json
from typing import Union

from DB.database import engineconn, azureBlobStorage, rabbitmq
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


async def existPostPicture_azure(name):
    isExist = await azureBlobStorage.exist(azureBlobStorage, "post-picture", name)

    if(isExist == False):
        return False
    elif(isExist == -1):
        return -1
    elif(isExist == 1):
        return 1


async def existUserProfilePicture_azure(name):
    isExist = await azureBlobStorage.exist(azureBlobStorage, "user-profile-picture", name)

    if(isExist == False):
        return False
    elif(isExist == -1):
        return -1
    elif(isExist == 1):
        return 1


async def getLastPostNumber():
    try:
        postNumber = list(session.execute(text('SELECT MAX(postNumber) FROM postInfo')).fetchone())
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return False

    session.close()
    return postNumber[0]

async def getLatestPostList(targetPostNumber: int, numberOfPost: int):
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
                'lostTime', lostTime,\
                'lostPlace', lostPlace,\
                'views', views,\
                'numberOfChat', numberOfChat,\
                'content', content,\
                'disabled', disabled\
                ) FROM postInfo WHERE postNumber < {targetPostNumber} AND disabled != 1 ORDER BY postNumber DESC"
        )))
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return False
    try:
        for i in range(numberOfPost):
            postList.append(json.loads(value[i][0]))
    except IndexError:
        pass
    session.close()
    return postList

async def getNearestPostList(locationX: Union[float, int], locationY: Union[float, int], distance: Union[float, int], numberOfPost: int):
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
            'lostTime', lostTime,\
            'lostPlace', lostPlace,\
            'views', views,\
            'numberOfChat', numberOfChat,\
            'content', content,\
            'disabled', disabled\
            ),\
            (6371*acos(cos(radians({locationY}))*cos(radians(locationY))*cos(radians(locationX)-radians({locationX}))\
            +sin(radians({locationY}))*sin(radians(locationY))))AS distance\
            FROM postInfo\
            HAVING distance >= {distance} AND distance <= {distance+5}\
            AND disabled != 1\
            ORDER BY distance\
            "
        )))
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
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
        session.rollback()
        session.close()
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
        session.rollback()
        session.close()
        return -2
    session.close()
    if(post == None):
        return -1
    elif(post["disabled"] == True):
        return 0
    return post

async def getPostPictureList(postNumber: int):
    try:
        pictureList = (list(session.execute(text(f"SELECT pictureNumber FROM postPicture WHERE postNumber = {postNumber};"))))
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.getPostPictureList]",type(e),e)
        session.rollback()
        session.close()
        return 0
    session.close()

    result = []
    for i in range(len(pictureList)):
        result.append(pictureList[i][0])

    return result

async def getPostPictureURLListDB(pictureList: list[int]):
    try:
        urlList = session.execute(text(
            f"SELECT JSON_OBJECT(\
                'postNumber', postNumber,\
                'pictureNumber', pictureNumber,\
                'imageURL', imageURL\
                ) FROM postPicture\
                WHERE postNumber IN ({str(pictureList)[1:-1]});"
        ))
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.getPostPictureURLListDB]",type(e),e)
        session.rollback()
        session.close()
        return 0
    
    session.close()

    urlList = list(urlList)
    result = []
    for i in range(len(urlList)):
        result.append(json.loads(urlList[i][0]))
    return result

async def getPostPictureDB(postNumber, pictureNumber):
    
    try:
        url = session.query(postPicture).filter(postPicture.postNumber == postNumber, postPicture.pictureNumber == pictureNumber).first().imageURL
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.getPostPictureDb]",type(e),e)
        session.rollback()
        session.close()
        return 0
    session.close()
    return url


async def getUserPictureDB(userNumber):
    try:
        url = session.query(userProfilePicture).filter(userProfilePicture.userNumber == userNumber).first().imageURL
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.getUserPictureDB]",type(e),e)
        session.close()
        return False
    session.close()
    return url


async def getReviewDB_reviewNumber(reviewNumber):
    try:
        review = jsonable_encoder(session.query(reviewInfo).get(reviewNumber))
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    session.close()
    if(review == None):
        return -1
    elif(review["disabled"] == True):
        return 0
    else:
        return review


async def getReviewDB_author(authorUserNumber, chatRoomNumber):
    try:
        review = session.query(reviewInfo).filter(reviewInfo.authorUserNumber == authorUserNumber, reviewInfo.chatRoomNumber == chatRoomNumber).first()
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.getReviewDB_author]",type(e),e)
        session.rollback()
        session.close()
        return False
    session.close()
    return review


async def getReviewListDB(userNumber: int):
    reviewList = []
    try:
        reviewList = list(session.execute(text(f"SELECT reviewNumber FROM reviewInfo WHERE targetUserNumber = {userNumber}")))
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.getReviewListDB]",type(e),e)
        session.rollback()
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
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.getChatRoomInfoDB]",type(e),e)
        session.rollback()
        session.close()
        return False
    session.close()
    return chatRoomInfo


async def emailToUserNumber(requestEmail) -> int:
    try:
        result = (session.query(userInfo).filter(userInfo.email == requestEmail).all())[0].userNumber
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
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
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.createUserInfo]",type(e),e)
        session.rollback()
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
        lostTime = post["lostTime"],
        lostPlace = post["lostPlace"],
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
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.createPostInfo]",type(e),e)
        session.rollback()
        session.close()
        return False
    session.close()

    info = await getPostInfo(postNumber[0])
    if(info == -2):
        return -2
    return info


async def createPostPictureURL_DB(url, postNumber, pictureNumber):

    pictureList = await getPostPictureList(postNumber)
    if(pictureList == -2):
        return -2

    if(pictureNumber in pictureList):
        print("[DB Error - DBdataLib.createPostPictureURL_DB(1)] pictureNumber already in there.")
        return False

    data = postPicture(
        postNumber = postNumber,
        pictureNumber = pictureNumber,
        imageURL = url
    )
    try:
        session.add(data)
        session.commit()
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.createPostPictureURL_DB(2)]",type(e),e)
        session.rollback()
        session.close()
        return False
    session.close()
    return True


async def createPostPicture_azure(file, postNumber, pictureNumber):
    name = str(postNumber)+"-"+str(pictureNumber)+".jpeg"
    isExistInAzure = await existPostPicture_azure(name)

    if(isExistInAzure == 1):
        print("[AZURE Error - DBdataLib.createPostPicture_azure(1)] pictureNumber already in there.")
        return -1
    elif(isExistInAzure == False):
        return False


    imageURL = await azureBlobStorage.upload(azureBlobStorage, container="post-picture", name=name, file=file)
    if(imageURL):
        return imageURL
    else:
        return False



# #not use
# async def createPostPicture(file, postNumber, pictureNumber):
#     data = postPicture(
#         postNumber = postNumber,
#         pictureNumber = pictureNumber,
#         data = file
#     )

#     pictureList = await getPostPictureList(postNumber)
#     if(pictureList == -2):
#         return -2

#     if(pictureNumber in pictureList):
#         print("[DB Error - DBdataLib.createPostPicture(1)] pictureNumber already in there.")
#         return False

#     try:
#         session.add(data)
#         session.commit()
#     except OperationalError:
#         print(f"[{datetime.now()}] DATABASE DOWN")
#         session.rollback()
#         session.close()
#         return -2
#     except Exception as e:
#         print("[DB Error - DBdataLib.createPostPicture(2)]",type(e),e)
#         session.rollback()
#         session.close()
#         return False
#     session.close()
#     return True

async def existUserProfilePictureDB(userNumber: int):
    isExist = session.execute(session.query(session.query(userProfilePicture).filter(userProfilePicture.userNumber==userNumber).exists())).all()[0][0]
    session.close()
    return isExist


async def createUserPictureURL_DB(url, userNumber: int):

    isExist = await existUserProfilePictureDB(userNumber)
    if(isExist):
        return -1

    data = userProfilePicture(
        userNumber = userNumber,
        imageURL = url
    )
    try:
        session.add(data)
        session.commit()
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.createUserPictureURL_DB]",type(e),e)
        session.rollback()
        session.close()
        return False
    
    session.close()
    return True


async def createUserPicture_azure(file, userNumber):
    name = str(userNumber)+".jpeg"
    isExistInAzure = await existUserProfilePicture_azure(name)

    if(isExistInAzure == 1):
        print("[AZURE Error - DBdataLib.createUserPicture_azure] userProfilePicture already in there.")
        return -1
    elif(isExistInAzure == False):
        return False

    imageURL = await azureBlobStorage.upload(azureBlobStorage, container="user-profile-picture", name=name, file=file)
    if(imageURL):
        return imageURL
    else:
        return False


# #not use
# async def createUserPictureDB(file, userNumber):
#     data = userProfilePicture(
#         userNumber = userNumber,
#         data = file
#     )
#     isPictureExist = await getUserPictureDB(userNumber)
#     if(isPictureExist == -2):
#         return -2
#     if(isPictureExist):
#         print("[DB Error - DBdataLib.createUserPictureDB(1)] userNumber already in DB.")
#         return False

#     try:
#         session.add(data)
#         session.commit()
#     except OperationalError:
#         print(f"[{datetime.now()}] DATABASE DOWN")
#         session.rollback()
#         session.close()
#         return -2
#     except Exception as e:
#         print("[DB Error - DBdataLib.createUserPictureDB(2)]",type(e),e)
#         session.rollback()
#         session.close()
#         return False
#     session.close()
#     return True


async def createReviewDB(reviewData: dict):
    data = reviewInfo(
        authorUserNumber = reviewData["authorUserNumber"],
        targetUserNumber = reviewData["targetUserNumber"],
        reviewDate = datetime.now(),
        rate = reviewData["rate"],
        content = reviewData["content"],
        chatRoomNumber = reviewData["chatRoomNumber"],
        disabled = False
    )
    try:
        session.add(data)
        session.commit()
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.createReviewDB(1)]",type(e),e)
        session.rollback()
        session.close()
        return False
    session.close()

    try:
        reviewNumber = list(session.execute(text("SELECT LAST_INSERT_ID() FROM reviewInfo")).fetchone())
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
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
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.createChatRoomDB]",type(e),e)
        session.rollback()
        session.close()
        return False
    session.close()

    try:
        chatRoomNumber = list(session.execute(text("SELECT LAST_INSERT_ID() FROM chatInfo")).fetchone())
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
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
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.updateUserInfo]",type(e),e)
        session.rollback()
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
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.updatePostInfo]",type(e),e)
        session.rollback()
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
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.updateReviewDB]",type(e),e)
        session.rollback()
        session.close()
        return 0
    session.close()
    return review["reviewNumber"]

# #not use
# async def updateChatRoomInfoDB(chatRoom: dict):
#     try:
#         session.query(chatInfo).filter(chatInfo.chatRoomNumber == chatRoom["chatRoomNumber"]).update(chatRoom)
#         session.commit()
#     except OperationalError:
#         print(f"[{datetime.now()}] DATABASE DOWN")
#         session.rollback()
#         session.close()
#         return -2
#     except Exception as e:
#         print("[DB Error - DBdataLib.updateChatRoomInfoDB]",type(e),e)
#         session.rollback()
#         session.close()
#         return False
#     session.close()
#     return chatRoom["chatRoomNumber"]


async def raisePoint(userNumber: int):
    try:
        session.execute(text(f"update userInfo set point = userInfo.point + 10 where userNumber = {userNumber}"))
        session.commit()
        session.close()
        return True
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.raisePoint]",type(e),e)
        session.rollback()
        session.close()
        return 0


async def changePostingDisable(postNumber: int):
    try:
        session.execute(text(f"update postInfo set disabled = 1 where postNumber = {postNumber}"))
        session.commit()
        session.close()
        return True
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.changePostingDisable]",type(e),e)
        session.rollback()
        session.close()
        return 0



async def deleteUserInfo(userNumber: int):
    try:
        session.delete(session.query(userInfo).filter(userInfo.userNumber == userNumber).first())
        session.commit()
        session.close()
        return 1
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.deleteUserInfo]",type(e),e)
        session.rollback()
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
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.deletePostInfo]",type(e),e)
        session.rollback()
        session.close()
        return 0
    

async def deletePostPictureURL_DB(postNumber, pictureNumber):
    try:
        session.delete(session.query(postPicture).filter(postPicture.postNumber == postNumber, postPicture.pictureNumber == pictureNumber).first())
        session.commit()
        session.close()
        return True
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.deletePostPictureURL_DB]",type(e),e)
        session.rollback()
        session.close()
        return False
    

async def deletePostPicture_azure(postNumber, pictureNumber):
    name = str(postNumber)+"-"+str(pictureNumber)+".jpeg"
    try:
        isDeleted = await azureBlobStorage.delete(azureBlobStorage, "post-picture", name)
    except Exception as e:
        print("[AZURE Error - DBdataLib.deletePostPicture_azure]",type(e),e)
        return False
    if(isDeleted == -1):
        return -1
    elif(isDeleted):
        return True
    else:
        return False

# #not use
# async def deletePostPicture(postNumber, pictureNumber):
#     try:
#         session.delete(session.query(postPicture).filter(postPicture.postNumber == postNumber, postPicture.pictureNumber == pictureNumber).first())
#         session.commit()
#         session.close()
#         return True
#     except OperationalError:
#         print(f"[{datetime.now()}] DATABASE DOWN")
#         session.rollback()
#         session.close()
#         return -2
#     except Exception as e:
#         print("[DB Error - DBdataLib.deletePostPicture]",type(e),e)
#         session.rollback()
#         session.close()
#         return False
    
async def deletePostPictureAll_DB(postNumber: int):
    try:
        session.execute(text(f"DELETE FROM postPicture WHERE postNumber = {str(postNumber)};"))
        session.commit()
        session.close()
        return True
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.deletePostPictureAll]",type(e),e)
        session.rollback()
        session.close()
        return False
    

# 최적화!!!
async def deletePostPictureAll_azure(postNumber: int):
    pictureList = await getPostPictureList(postNumber)
    
    for i in pictureList:
        try:
            isDeleted = await azureBlobStorage.delete(azureBlobStorage, "post-picture", str(postNumber)+"-"+str(i)+".jpeg")
        except Exception as e:
            print("[AZURE Error - DBdataLib.deletePostPictureAll_azure]",type(e),e)
            return False
        
        if(isDeleted == -1):
            return -1
        elif(isDeleted != True):
            return False
        
    return True


async def deleteUserProfilePictureURL_DB(userNumber):
    try:
        session.delete(session.query(userProfilePicture).filter(userProfilePicture.userNumber == userNumber).first())
        session.commit()
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.deleteUserProfilePictureURL_DB]",type(e),e)
        session.rollback()
        session.close()
        return False
    
    session.close()
    return True


async def deleteUserProfilePicture_azure(userNumber):
    name = str(userNumber)+".jpeg"
    try:
        isDeleted = await azureBlobStorage.delete(azureBlobStorage, "user-profile-picture", name)
    except Exception as e:
        print("[AZURE Error - DBdataLib.deleteUserProfilePicture_azure]",type(e),e)
        return False
    if(isDeleted == -1):
        return -1
    elif(isDeleted != True):
        return False
    
    return True
    
    
# #not use
# async def deleteUserProfilePicture(userNumber):
#     try:
#         session.delete(session.query(userProfilePicture).filter(userProfilePicture.userNumber == userNumber).first())
#         session.commit()
#         session.close()
#         return True
#     except OperationalError:
#         print(f"[{datetime.now()}] DATABASE DOWN")
#         session.rollback()
#         session.close()
#         return -2
#     except Exception as e:
#         print("[DB Error - DBdataLib.deleteUserProfilePicture]",type(e),e)
#         session.rollback()
#         session.close()
#         return False
    
async def deleteReviewDB(reviewNumber: int):
    try:
        session.delete(session.query(reviewInfo).filter(reviewInfo.reviewNumber == reviewNumber).first())
        session.commit()
        session.close()
        return True
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.deleteReviewDB]",type(e),e)
        session.rollback()
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
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.deleteChatRoomInfoDB]",type(e),e)
        session.rollback()
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
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.deleteChatRecodeDB]",type(e),e)
        session.rollback()
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
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.viewsPlusOne]",type(e),e)
        session.rollback()
        session.close()
        return 0
    
async def ratePlus(userNumber: int, rate: int):
    try:
        session.execute(text(f"update userInfo set rateSum  = userInfo.rateSum + {rate}, countOfRate = userInfo.countOfRate + 1 where userNumber = {userNumber}"))
        #session.execute(text(f"update userInfo set countOfRate = userInfo.countOfRate + 1 where userNumber = {userNumber}"))
        session.commit()
        session.close()
        return True
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.ratePlus]",type(e),e)
        session.rollback()
        session.close()
        return False
    

async def searchInDB_recent(find: str, numberOfPost: int):
    postList = []
    try:
        result = list(session.execute(text(
            f"SELECT JSON_OBJECT(\
                'postNumber',postNumber,\
                'postName', postName,\
                'postUserNumber', postUserNumber,\
                'postDate', postDate,\
                'postType', postType,\
                'postCategory', postCategory,\
                'locationX', locationX,\
                'locationY', locationY,\
                'lostTime', lostTime,\
                'lostPlace', lostPlace,\
                'views', views,\
                'numberOfChat', numberOfChat,\
                'content', content,\
                'disabled', disabled\
                ) FROM postInfo WHERE MATCH(postName, content, lostPlace) AGAINST(\'{find}\' IN BOOLEAN MODE) AND disabled != 1 ORDER BY postNumber DESC LIMIT {numberOfPost}"
        )).all())
        #result = session.query(session.query(postInfo).filter(postInfo.postName.match({find + '*'}), postInfo.content.match({find + '*'}), postInfo.lostPlace.match({find + '*'})).all())
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.searchInDB]",type(e),e)
        session.rollback()
        session.close()
        return False
    
    try:
        for i in range(numberOfPost):
            postList.append(json.loads(result[i][0]))
    except IndexError:
        pass
    return postList



async def searchInDB_exact(find: str, numberOfPost: int):
    postList = []
    try:
        result = list(session.execute(text(
            f"SELECT JSON_OBJECT(\
                'postNumber',postNumber,\
                'postName', postName,\
                'postUserNumber', postUserNumber,\
                'postDate', postDate,\
                'postType', postType,\
                'postCategory', postCategory,\
                'locationX', locationX,\
                'locationY', locationY,\
                'lostTime', lostTime,\
                'lostPlace', lostPlace,\
                'views', views,\
                'numberOfChat', numberOfChat,\
                'content', content,\
                'disabled', disabled\
                ) FROM postInfo WHERE MATCH(postName, content, lostPlace) AGAINST(\'{find}\' IN BOOLEAN MODE) AND disabled != 1 LIMIT {numberOfPost}"
        )).all())
        #result = session.query(session.query(postInfo).filter(postInfo.postName.match({find + '*'}), postInfo.content.match({find + '*'}), postInfo.lostPlace.match({find + '*'})).all())
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.searchInDB]",type(e),e)
        session.rollback()
        session.close()
        return False
    
    try:
        for i in range(numberOfPost):
            postList.append(json.loads(result[i][0]))
    except IndexError:
        pass
    
    return postList



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
#         session.rollback()
#         session.close()
#         return -2
#     except Exception as e:
#         print("[DB Error - DBdataLib.rateSubtrack]",type(e),e)
#         session.rollback()
#         session.close()
#         return False