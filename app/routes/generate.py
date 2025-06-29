from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def test_generate():
    return {"message": "Generate route working"}
