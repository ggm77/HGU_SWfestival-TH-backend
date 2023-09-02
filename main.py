"""
2023.08.30 started


uvicorn main:app --reload --host=0.0.0.0 --port=8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1 import user, token, verification

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

