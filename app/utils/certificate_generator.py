from PIL import Image, ImageDraw, ImageFont
from email.message import EmailMessage
import smtplib
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
import threading

load_dotenv()
print("✅ certificate_generator module loaded")

OUTPUT_DIR = "generated_certificates"
os.makedirs(OUTPUT_DIR, exist_ok=True)

FONT_MAP = {
    "Roboto": {"regular": "Poppins-Regular.ttf", "bold": "Poppins-Black.ttf"},
    "Arimo": {"regular": "Poppins-Regular.ttf", "bold": "Poppins-Black.ttf"},
    "Tinos": {"regular": "Poppins-Regular.ttf", "bold": "Poppins-Black.ttf"},
    "Poppins": {"regular": "Poppins-Regular.ttf", "bold": "Poppins-Black.ttf"},
}

def get_font(font_name: str, is_bold: bool, font_size: int) -> ImageFont.FreeTypeFont:
    style = "bold" if is_bold else "regular"
    font_file = FONT_MAP.get(font_name, FONT_MAP["Roboto"]).get(style, FONT_MAP["Roboto"]["regular"])
    font_path = os.path.join("fonts", font_file)
    try:
        return ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"⚠️ Font file not found at '{font_path}'. Using default font.")
        return ImageFont.load_default()

# --- THIS FUNCTION CONTAINS THE CRITICAL FIX ---
def draw_certificate(template_path: str, output_path: str, data: dict, placeholders):
    """Draw text on the certificate template using settings from the frontend."""
    cert = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(cert)
    img_width, img_height = cert.size
    
    for field, settings in placeholders.items():
        value = str(data.get(field, field))

        # --- FIX: Use object dot notation (.key) instead of dictionary brackets (['key']) ---
        font_size = int(settings.font_size)
        font_name = settings.font
        bold = settings.bold
        x, y = settings.x, settings.y
        color = settings.color
        # --- END FIX ---
        
        font = get_font(font_name, bold, font_size)
        
        text_bbox = draw.textbbox((0, 0), value, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        
        max_width = img_width * 0.9
        if text_width > max_width:
            scale_factor = max_width / text_width
            new_font_size = int(font_size * scale_factor)
            font = get_font(font_name, bold, new_font_size)
        
        draw.text((x, y), value, fill=color, font=font, anchor="la")

    cert.save(output_path)
    print(f"💾 Certificate saved: {output_path}")

def generate_certificates_only(data_list, template_path, placeholders, is_preview: bool = False):
    """Generate certificates with manually defined font sizes from the frontend."""
    errors = []
    generated_path = None
    
    for row in data_list:
        try:
            name = row.get("Name", "Unnamed")
            file_name = f"{name}_preview.png" if is_preview else f"{name}.png"
            cert_path = os.path.join(OUTPUT_DIR, file_name)
            
            draw_certificate(template_path, cert_path, row, placeholders)

            if is_preview:
                generated_path = cert_path
                break
        except Exception as e:
            print(f"❌ ERROR generating for {row.get('Name', 'Unknown')}: {e}")
            errors.append(f"{row.get('Name', 'Unknown')}: {str(e)}")
            
    return generated_path if is_preview else errors

# In certificate_generator.py

def send_certificates_only(data_list):
    """Connects once and sends all emails in a parallel batch, SAFELY."""
    smtp_host = os.getenv("EMAIL_HOST")
    smtp_port = int(os.getenv("EMAIL_PORT", 587))
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")

    success_logs = []
    error_logs = []
    log_lock = threading.Lock()
    # --- FIX: Create a new lock specifically for the server connection ---
    server_lock = threading.Lock()

    # The helper function now accepts the server_lock
    def send_single_email(server, lock, row):
        name = row.get("Name", "Unnamed")
        email = row.get("Email")
        try:
            print(f"🔹 Preparing email for {name} <{email}>")
            cert_path = os.path.join(OUTPUT_DIR, f"{name}.png")
            if not os.path.exists(cert_path):
                raise FileNotFoundError(f"Certificate not found for {name}")

            msg = EmailMessage()
            msg["From"] = sender_email
            msg["To"] = email
            msg["Subject"] = "You're In! Welcome to the PORT:80 Crew!"
            msg.set_content(f"Hi {name},\n\nCongratulations and welcome!")

            with open(cert_path, "rb") as f:
                msg.add_attachment(f.read(), maintype="image", subtype="png", filename=f"{name}.png")

            # --- FIX: Use the lock to ensure only one thread sends at a time ---
            with lock:
                server.send_message(msg)
            # --- END FIX ---
            
            with log_lock:
                success_logs.append(f"✅ Email successfully sent to {email}")
        except Exception as e:
            with log_lock:
                error_logs.append(f"❌ Failed to send to {email}: {e}")

    print(f"📧 Connecting to SMTP server {smtp_host}:{smtp_port}...")
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            print("✅ SMTP Login Successful. Starting parallel email dispatch...")

            with ThreadPoolExecutor(max_workers=5) as executor:
                # We now pass the server_lock to each worker
                for row in data_list:
                    executor.submit(send_single_email, server, server_lock, row)
        
        print("✅ All email tasks submitted. Waiting for completion...")
    except Exception as e:
        print(f"❌ A critical error occurred with the SMTP connection: {e}")
        error_logs.append(f"CRITICAL: Could not connect or login to SMTP server: {e}")

    print("📌 Email sending process completed")
    print(f"✅ Successes: {len(success_logs)}, ❌ Errors: {len(error_logs)}")
    
    if error_logs:
        print("\n--- ERRORS ---")
        for err in error_logs:
            print(err)

    return {"successes": success_logs, "errors": error_logs}