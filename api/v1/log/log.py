from fastapi import APIRouter, HTTPException, status, UploadFile, Response
from fastapi.responses import JSONResponse

from lib.lib import *
from lib.dataClass import *

router = APIRouter(prefix="/api/v1")

