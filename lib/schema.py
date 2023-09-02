from pydantic import BaseModel

class tokenRequest(BaseModel):
    email: str
    password: str

class registRequest(BaseModel):
    username: str
    email: str
    password: str
    locationX: float
    locationY: float

class registResponse(BaseModel):#not use
    username: str
    userNumber: int
    userType: str
    signUpDate: str
    email: str
    locationX: float
    locationY: float
    point: int
    disabled: bool


class userinfoRequest(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class deleteuserRequest(BaseModel):
    email: str
    password: str
    access_token: str
    token_type: str
    refresh_token: str

class updateuserRequest(BaseModel):
    email: str
    password: str
    locationX: float
    locationY: float
    access_token: str
    token_type: str
    refresh_token: str

class verificationRequest(BaseModel):
    password: str
    access_token: str
    token_type: str
    refresh_token: str

class disableuserRequest(BaseModel):
    targetUserNumber: int
    access_token: str
    token_type: str
    refresh_token: str

class enableuserRequest(BaseModel):
    targetUserNumber: int
    access_token: str
    token_type: str
    refresh_token: str