from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
import os, shutil, json
from app.utils.excel_reader import extract_excel_data
from app.utils.dynamic_certificate_generator import generate_certificates

router = APIRouter()

@router.post("/certificates")
async def generate_certificates_route(
    excel_file: UploadFile = File(...),
    template_image: UploadFile = File(...),
    config_json: str = Form(...)
):
    os.makedirs("temp", exist_ok=True)

    excel_path = f"temp/{excel_file.filename}"
    template_path = f"temp/{template_image.filename}"

    with open(excel_path, "wb") as ef:
        shutil.copyfileobj(excel_file.file, ef)

    with open(template_path, "wb") as tf:
        shutil.copyfileobj(template_image.file, tf)

    # Extract Excel data
    data = extract_excel_data(excel_path)

    # Parse config JSON
    try:
        config = json.loads(config_json)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format for config."}
    
    # Handle case if config is still a string (e.g., double encoded)
    if isinstance(config, str):
        try:
            config = json.loads(config)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid config JSON format")

    # Generate certificates
    zip_path = generate_certificates(data, template_path, config)

    return FileResponse(zip_path, media_type="application/zip", filename="certificates.zip")
