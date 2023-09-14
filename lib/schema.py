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

class uploadpostpictureRequest(BaseModel):
    postNumber: int
    pictureNumber: int
    access_token: str
    token_type: str
    refresh_token: str

class createreviewRequest(BaseModel):
    targetUserNumber: int
    rate: int
    content: str
    postNumber: int
    access_token: str
    token_type: str
    refresh_token: str

class createchatroomRequest(BaseModel):
    postUserNumber: int
    postNumber: int
    access_token: str
    token_type: str
    refresh_token: str

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
    rateSum: Union[int, None]
    countOfRate: Union[int, None]
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

class updatereviewRequest(BaseModel):
    reviewNumber: int
    authorUserNumber: Union[int, None]
    targetUserNumber: Union[int, None]
    reviewDate: Union[str, None]
    rate: Union[int, None]
    content: Union[str, None]
    postNumber: Union[int, None]
    disabled: Union[bool, None]
    access_token: str
    token_type: str
    refresh_token: str


class deletepostingRequest(BaseModel):
    postNumber: int
    access_token: str
    token_type: str
    refresh_token: str

class deleteuser_adminRequest(BaseModel):
    targetUserNumber: int
    access_token: str
    token_type: str
    refresh_token: str

class disablepostRequest(BaseModel):
    targetPostNumber: int
    access_token: str
    token_type: str
    refresh_token: str

class deletechatroom_adminRequest(BaseModel):
    chatRoomNumber: int
    access_token: str
    token_type: str
    refresh_token: str

class enablepostRequest(BaseModel):
    targetPostNumber: int
    access_token: str
    token_type: str
    refresh_token: str


class disablereviewRequest(BaseModel):
    reviewNumber: int
    access_token: str
    token_type: str
    refresh_token: str


class enablereviewRequest(BaseModel):
    reviewNumber: int
    access_token: str
    token_type: str
    refresh_token: str


class updateposting_adminRequest(BaseModel):
    postNumber: int
    postName: Union[str, None]
    postDate: Union[str, None]
    postType: Union[str, None]
    postCategory: Union[str, None]
    locationX: Union[float, None]
    locationY: Union[float, None]
    content: Union[str, None]
    disabled: Union[bool, None]
    access_token: str
    token_type: str
    refresh_token: str

class deletepostpicture_adminRequest(BaseModel):
    postNumber: int
    pictureNumber: int
    access_token: str
    token_type: str
    refresh_token: str

class deleteposting_adminRequest(BaseModel):
    postNumber: int
    access_token: str
    token_type: str
    refresh_token: str


class deletepictureRequest(BaseModel):
    postNumber: int
    pictureNumber: int
    access_token: str
    token_type: str
    refresh_token: str

class deleteuserpictureRequest(BaseModel):
    userNumber: int
    access_token: str
    token_type: str
    refresh_token: str

class deleteuserpicture_adminRequest(BaseModel):
    userNumber: int
    access_token: str
    token_type: str
    refresh_token: str

class deletereviewRequest(BaseModel):
    reviewNumber: int
    access_token: str
    token_type: str
    refresh_token: str