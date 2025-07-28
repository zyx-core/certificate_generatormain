from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict
import base64, tempfile
import pandas as pd
from app.utils.certificate_generator import generate_certificates_only, send_certificates_only
from fastapi.responses import FileResponse

router = APIRouter()

# --- UPDATED: Add 'font' property ---
class PlaceholderProperties(BaseModel):
    x: float
    y: float
    font_size: float
    color: str
    bold: bool
    font: str = "Roboto" # Add font with a default value

class CertificateData(BaseModel):
    placeholders: Dict[str, PlaceholderProperties]
    excel_data: List[Dict[str, str]]
    template_bytes: str

@router.post("/generate-and-send-uploaded")
async def generate_and_send_uploaded(data: CertificateData):
    try:
        image_data = base64.b64decode(data.template_bytes)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_template:
            tmp_template.write(image_data)
            template_path = tmp_template.name

        records = data.excel_data
        
        errors_gen = generate_certificates_only(
            data_list=records, 
            template_path=template_path, 
            placeholders=data.placeholders
        )
        
        email_logs = send_certificates_only(records)

        return {
            "message": "Process completed.",
            "details": {
                "generation_errors": errors_gen,
                "email_successes": email_logs["successes"],
                "email_errors": email_logs["errors"],
            }
        }

    except Exception as e:
        import traceback
        print("❌ Exception in /generate-and-send-uploaded:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-preview")
async def generate_live_preview(data: CertificateData):
    try:
        image_data = base64.b64decode(data.template_bytes)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_template:
            tmp_template.write(image_data)
            template_path = tmp_template.name

        preview_data_row = data.excel_data[0] if data.excel_data else {}

        preview_image_path = generate_certificates_only(
            data_list=[preview_data_row], 
            template_path=template_path, 
            placeholders=data.placeholders,
            is_preview=True
        )
        
        if not preview_image_path:
             raise HTTPException(status_code=500, detail="Preview generation failed.")

        return FileResponse(preview_image_path)

    except Exception as e:
        import traceback
        print(f"❌ Exception in /generate-preview: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))