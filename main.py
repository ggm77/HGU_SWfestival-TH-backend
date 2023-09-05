"""
2023.08.30 started

uvicorn main:app --reload --host=0.0.0.0 --port=8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.admin import posting as admin_posting, user as admin_user
from api.v1.posting import posting, list as posting_list, picture as posting_picture
from api.v1.token import token
from api.v1.user import user
from api.v1.verification import verification

app = FastAPI()

origins = [
    #frontend url
    "http://localhost:3000",
    "localhost:3000",
    "http://raspinas.iptime.org:3000",
    "raspinas.iptime.org:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(user.router)
app.include_router(token.router)
app.include_router(verification.router)
app.include_router(posting.router)
app.include_router(posting_list.router)
app.include_router(posting_picture.router)
app.include_router(admin_user.router)
app.include_router(admin_posting.router)


