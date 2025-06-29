from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/", response_class=JSONResponse)
def test_upload() -> dict:
    return {"message": "Upload route working"}
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def test_upload():
    return {"message": "Upload route working"}
