"""
2023.08.30 started

"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os

from api.v1.admin import posting as admin_posting, user as admin_user, review as admin_review, chat as admin_chat
from api.v1.posting import posting, list as posting_list, picture as posting_picture
from api.v1.token import token
from api.v1.user import user, picture as user_picture
from api.v1.review import review, list as review_list
from api.v1.verification import verification
from api.v1.ws import ws
from api.v1.chat import chat
from api.v1.socket_IO.sockets import sio_app

app = FastAPI()

origins = [
    #frontend url
    "http://localhost:3000",
    "localhost:3000",
    "http://raspinas.iptime.org:3000",
    "raspinas.iptime.org:3000",
    "172.17.218.152:51175"
]

app.add_middleware(
    CORSMiddleware,
    #allow_origins=origins,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.mount("/api/v1/socket_IO", app=sio_app)
app.include_router(user.router)
app.include_router(user_picture.router)
app.include_router(token.router)
app.include_router(verification.router)
app.include_router(posting.router)
app.include_router(posting_list.router)
app.include_router(posting_picture.router)
app.include_router(review.router)
app.include_router(review_list.router)
app.include_router(admin_user.router)
app.include_router(admin_posting.router)
app.include_router(admin_review.router)
app.include_router(admin_chat.router)
# app.include_router(ws.router)
app.include_router(chat.router)




templates = Jinja2Templates(directory="assets/testFrontPage")
@app.get("/test/wsTest/createchat")
async def wbTest(request : Request):
    return  templates.TemplateResponse("testWS.html",{"request":request})

#not use - do it on frontend
# @app.get("/test/wsTest/getchat")
# async def wbTestGetchat(request: Request):
#     return templates.TemplateResponse("testWSgetchat.html",{"request":request})



@app.get("/test")
async def test():

    return {"test":"success"}

