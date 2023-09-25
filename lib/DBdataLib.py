from fastapi.encoders import jsonable_encoder
from datetime import timedelta, datetime
from sqlalchemy import text

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


async def getReviewDB_reviewNumber(reviewNumber):
    review = jsonable_encoder(session.query(reviewInfo).get(reviewNumber))
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
    except Exception as e:
        print("[DB Error]",e)
        session.close()
        return False
    session.close()
    return chatRoomInfo





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
        postNumber = list(session.execute(text('SELECT LAST_INSERT_ID() FROM postInfo')).fetchone())
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
    except Exception as e:
        print("[DB Error]",e)
        session.close()
        return False
    session.close()

    reviewNumber = list(session.execute(text("SELECT LAST_INSERT_ID() FROM reviewInfo")).fetchone())
    return await getReviewDB_reviewNumber(reviewNumber[0])

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
    except Exception as e:
        print("[DB Error]",e)
        session.close()
        return False
    session.close()

    chatRoomNumber = list(session.execute(text("SELECT LAST_INSERT_ID() FROM chatInfo")).fetchone())
    return await getChatRoomInfoDB(chatRoomNumber[0])

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

async def updateReviewDB(review: dict):
    try:
        session.query(reviewInfo).filter(reviewInfo.reviewNumber == review["reviewNumber"]).update(review)
        session.commit()
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
    
async def deletePostPictureAll(postNumber):
    try:
        session.execute(text(f"DELETE FROM postPicture WHERE postNumber = {str(postNumber)};"))
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
    
async def deleteReviewDB(reviewNumber: int):
    try:
        session.delete(session.query(reviewInfo).filter(reviewInfo.reviewNumber == reviewNumber).first())
        session.commit()
        session.close()
        return True
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
    except Exception as e:
        print("[DB Error]", e)
        session.close()
        return 0
    
async def ratePlus(userNumber: int, rate: int):
    try:
        session.execute(text(f"update userInfo set rateSum  = userInfo.rateSum + {rate} where userNumber = {userNumber}"))
        session.execute(text(f"update userInfo set countOfRate = userInfo.countOfRate + 1 where userNumber = {userNumber}"))
        session.commit()
        session.close()
        return True
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
#     except Exception as e:
#         print("[DB Error]",e)
#         session.close()
#         return False