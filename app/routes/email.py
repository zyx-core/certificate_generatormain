from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
from app.utils.certificate_generator import generate_and_send_certificates
import tempfile
import shutil

router = APIRouter()

@router.post("/generate-and-send-uploaded")
async def generate_and_email_uploaded(
    excel_file: UploadFile = File(...),
    template_file: UploadFile = File(...)
):
    try:
        # Save uploaded files to temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_excel:
            shutil.copyfileobj(excel_file.file, tmp_excel)
            excel_path = tmp_excel.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_template:
            shutil.copyfileobj(template_file.file, tmp_template)
            template_path = tmp_template.name

        # Read Excel and convert to list of dicts
        df = pd.read_excel(excel_path)
        data = df.to_dict(orient="records")

        # Generate and send
        errors = generate_and_send_certificates(data, template_path)

        if errors:
            return JSONResponse(
                status_code=207,
                content={"message": "Some emails failed to send.", "errors": errors}
            )

        return {"message": "All certificates generated and emailed successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
