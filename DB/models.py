from sqlalchemy import Column, Boolean, VARCHAR, FLOAT, INTEGER, DATETIME
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
    disabled = Column(Boolean, nullable=False)


# class posting(Base):
#     __tablename__ = "posting"


# class review(Base):
#     __tablename__ = "review"


# class chat(Base):
#     __tablename__ = "chat"


# class chatHistory(Base):
#     __tablename__ = "chatHistory"