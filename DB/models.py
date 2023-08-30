from sqlalchemy import Column, Boolean, VARCHAR
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class userInfo(Base):
    __tablename__ = "userInfo"

    username = Column(VARCHAR, nullable=False, primary_key=True)
    hashed_password = Column(VARCHAR, nullable=False)
    userType = Column(VARCHAR, nullable=False)
    disabled = Column(Boolean, nullable=False)


class posting(Base):
    __tablename__ = "posting"


class review(Base):
    __tablename__ = "review"


class chat(Base):
    __tablename__ = "chat"


class chatHistory(Base):
    __tablename__ = "chatHistory"