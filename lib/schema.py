from pydantic import BaseModel

class tokenRequest(BaseModel):
    email: str
    password: str

class registRequest(BaseModel):
    username: str
    email: str
    password: str
    location: list[float]

class registResponse(BaseModel):#not use
    username: str
    userNumber: int
    userType: str
    signUpDate: str
    email: str
    locationX: float
    locationY: float
    chatList: list[int]
    point: int
    disabled: bool