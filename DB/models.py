from sqlalchemy import Column, Boolean, VARCHAR, FLOAT, INTEGER, DATETIME, PickleType, BLOB, TEXT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class userInfo(Base):
    __tablename__ = "userInfo"

    userNumber = Column(INTEGER, nullable=False, primary_key=True)
    username = Column(VARCHAR, nullable=False)
    hashed_password = Column(VARCHAR, nullable=False)
    userType = Column(VARCHAR, nullable=False)
    signUpDate = Column(DATETIME, nullable=False)
    email = Column(VARCHAR, nullable=False)
    locationX = Column(FLOAT, nullable=False)#Latitude : 위도
    locationY = Column(FLOAT, nullable=False)#longitude : 경도
    point = Column(INTEGER, nullable=False)
    rateSum = Column(INTEGER, nullable=False)
    countOfRate = Column(INTEGER, nullable=False)
    disabled = Column(Boolean, nullable=False)


class postInfo(Base):
    __tablename__ = "postInfo"

    postNumber = Column(INTEGER, nullable=False, primary_key=True)
    postName = Column(VARCHAR, nullable=False)
    postUserNumber = Column(INTEGER, nullable=False)
    postDate = Column(DATETIME, nullable=False)
    postType = Column(VARCHAR, nullable=False)
    postCategory = Column(VARCHAR, nullable=False)
    locationX = Column(FLOAT, nullable=False)
    locationY = Column(FLOAT, nullable=False)
    lostTime = Column(DATETIME, nullable=False)
    lostPlace = Column(VARCHAR, nullable=False)
    views = Column(INTEGER, nullable=False)
    numberOfChat = Column(INTEGER, nullable=False)
    content = Column(VARCHAR, nullable=False)
    disabled = Column(Boolean, nullable=False)


class postPicture(Base):
    __tablename__ = "postPicture"

    id = Column(INTEGER, nullable=False, primary_key=True)
    postNumber = Column(INTEGER, nullable=False)
    pictureNumber = Column(INTEGER, nullable=False)
    imageURL = Column(TEXT, nullable=False)


class userProfilePicture(Base):
    __tablename__ = "userProfilePicture"

    id = Column(INTEGER, nullable=False, primary_key=True)
    userNumber = Column(INTEGER, nullable=False)
    imageURL = Column(TEXT, nullable=False)


class reviewInfo(Base):
    __tablename__ = "reviewInfo"

    reviewNumber = Column(INTEGER, nullable=False, primary_key=True)
    authorUserNumber = Column(INTEGER, nullable=False)
    targetUserNumber = Column(INTEGER, nullable=False)
    reviewDate = Column(DATETIME, nullable=False)
    rate = Column(INTEGER, nullable=False)
    content = Column(VARCHAR, nullable=False)
    chatRoomNumber = Column(INTEGER, nullable=False)
    disabled = Column(Boolean, nullable=False)


class chatInfo(Base):
    __tablename__ = "chatInfo"

    chatRoomNumber = Column(INTEGER, nullable=False, primary_key=True)
    postNumber = Column(INTEGER, nullable=False)
    postUserNumber = Column(INTEGER, nullable=False)
    chatterNumber = Column(INTEGER, nullable=False)
    date = Column(DATETIME, nullable=False)


class chatRecodeInfo(Base):
    __tablename__ = "chatRecodeInfo"

    id = Column(INTEGER, nullable=False, primary_key=True)
    chatRoomNumber = Column(INTEGER, nullable=False)
    messageNumber = Column(INTEGER, nullable=False)
    authorUserNumber = Column(INTEGER, nullable=False)
    text = Column(VARCHAR, nullable=False)
    date = Column(DATETIME, nullable=False)
    readChat = Column(Boolean, nullable=False)