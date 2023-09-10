from sqlalchemy import Column, Boolean, VARCHAR, FLOAT, INTEGER, DATETIME, PickleType, BLOB
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
    views = Column(INTEGER, nullable=False)
    numberOfChat = Column(INTEGER, nullable=False)
    content = Column(VARCHAR, nullable=False)
    disabled = Column(Boolean, nullable=False)


class postPicture(Base):
    __tablename__ = "postPicture"

    id = Column(INTEGER, nullable=False, primary_key=True)
    postNumber = Column(INTEGER, nullable=False)
    pictureNumber = Column(INTEGER, nullable=False)
    data = Column(BLOB, nullable=False)


class userProfilePicture(Base):
    __tablename__ = "userProfilePicture"

    userNumber = Column(INTEGER, nullable=False, primary_key=True)
    data = Column(BLOB, nullable=False)


class reviewInfo(Base):
    __tablename__ = "reviewInfo"

    reviewNumber = Column(INTEGER, nullable=False, primary_key=True)
    authorUserNumber = Column(INTEGER, nullable=False)
    targetUserNumber = Column(INTEGER, nullable=False)
    reviewDate = Column(DATETIME, nullable=False)
    rate = Column(INTEGER, nullable=False)
    content = Column(VARCHAR, nullable=False)
    postNumber = Column(INTEGER, nullable=False)
    disabled = Column(Boolean, nullable=False)


# class chat(Base):
#     __tablename__ = "chat"


# class chatHistory(Base):
#     __tablename__ = "chatHistory"