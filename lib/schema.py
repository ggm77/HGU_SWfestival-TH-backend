from pydantic import BaseModel
from typing import Union

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
    email: Union[str, None]
    password: Union[str, None]
    locationX: Union[float, None]
    locationY: Union[float, None]
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

class changuserinfoRequest(BaseModel):
    userNumber: int
    username: Union[str, None]
    password: Union[str, None]
    userType: Union[str, None]
    signUpDate: Union[str, None]
    email: Union[str, None]
    locationX: Union[float, None]
    locationY: Union[float, None]
    point: Union[int, None]
    disabled: Union[bool, None]
    admin_access_token: str
    admin_token_type: str
    admin_refresh_token: str

class createpostingRequest(BaseModel):
    postName: str
    postType: str
    postCategory: str
    locationX: float
    locationY: float
    content: str
    access_token: str
    token_type: str
    refresh_token: str

class updatepostingRequest(BaseModel):
    postNumber: int
    postName: str
    postType: str
    postCategory: str
    locationX: float
    locationY: float
    content: str
    access_token: str
    token_type: str
    refresh_token: str

class deletepostingRequest(BaseModel):
    postNumber: int
    access_token: str
    token_type: str
    refresh_token: str