from PIL import Image, ImageDraw, ImageFont
from email.message import EmailMessage
import smtplib
import os
from dotenv import load_dotenv
<<<<<<< HEAD
from concurrent.futures import ThreadPoolExecutor
import threading
=======
>>>>>>> 6ff748039b0b480fb153db4de088e71996bfba7f

load_dotenv()
print("✅ certificate_generator module loaded")

OUTPUT_DIR = "generated_certificates"
os.makedirs(OUTPUT_DIR, exist_ok=True)

<<<<<<< HEAD
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
    
=======
# --- Font Map ---
FONT_MAP = {
    "Roboto": {
        "regular": "Roboto-Regular.ttf",
        "bold": "Roboto-Bold.ttf"
    },
    "Arimo": {
        "regular": "Arimo-VariableFont_wght.ttf",
        "bold": "Arimo-Bold.ttf"
    },
    "Tinos": {
        "regular": "Tinos-Regular.ttf",
        "bold": "Tinos-Bold.ttf"
    },
    "Poppins": {
        "regular": "Poppins-Regular.ttf",
        "bold": "Poppins-Bold.ttf"
    }
}

# --- BOOST font size to make text visible on high-res images ---
SCALE_BOOST = 3.0  # Adjust to 2.0 or 4.0 depending on image size and visibility

def draw_certificate(template_path, output_path, data, placeholders):
    """Draws text on the certificate template."""
    cert = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(cert)

    for field, settings in placeholders.items():
        value = str(data.get(field, ""))
        x = settings.x
        y = settings.y
        font_size = int(settings.font_size * SCALE_BOOST)
        color = settings.color
        font_name = settings.font
        is_bold = settings.bold
        
        font_style = "bold" if is_bold else "regular"
        font_file = FONT_MAP.get(font_name, FONT_MAP["Roboto"]).get(font_style, FONT_MAP["Roboto"]["regular"])
        font_path = os.path.join("fonts", font_file)

        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            print(f"⚠️ Font file not found at '{font_path}'. Falling back to default font.")
            font = ImageFont.load_default()

        draw.text((x, y), value, fill=color, font=font, anchor="mm")

    cert.save(output_path)

def generate_certificates_only(data_list, template_path, placeholders: dict, is_preview: bool = False):
    """Generates certificate images and returns a path for previews or errors for batches."""
    errors = []
    generated_path = None
>>>>>>> 6ff748039b0b480fb153db4de088e71996bfba7f
    for row in data_list:
        try:
            name = row.get("Name", "Unnamed")
            file_name = f"{name}_preview.png" if is_preview else f"{name}.png"
            cert_path = os.path.join(OUTPUT_DIR, file_name)
<<<<<<< HEAD
            
            draw_certificate(template_path, cert_path, row, placeholders)
=======

            abs_cert_path = os.path.abspath(cert_path)
            print(f"📄 Saving certificate to: {abs_cert_path}")

            draw_certificate(template_path, cert_path, row, placeholders)
            print(f"✅ Saved: {cert_path}")
>>>>>>> 6ff748039b0b480fb153db4de088e71996bfba7f

            if is_preview:
                generated_path = cert_path
                break
<<<<<<< HEAD
        except Exception as e:
            print(f"❌ ERROR generating for {row.get('Name', 'Unknown')}: {e}")
            errors.append(f"{row.get('Name', 'Unknown')}: {str(e)}")
            
    return generated_path if is_preview else errors

# In certificate_generator.py

def send_certificates_only(data_list):
    """Connects once and sends all emails in a parallel batch, SAFELY."""
=======

        except Exception as e:
            print(f"❌ ERROR generating for {row.get('Name', 'Unknown')}: {e}")
            errors.append(f"{row.get('Name', 'Unknown')}: {str(e)}")

    return generated_path if is_preview else errors

def send_certificates_only(data_list):
    """Sends certificates and returns a log of successes and errors."""
>>>>>>> 6ff748039b0b480fb153db4de088e71996bfba7f
    smtp_host = os.getenv("EMAIL_HOST")
    smtp_port = int(os.getenv("EMAIL_PORT", 587))
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")

    success_logs = []
    error_logs = []
<<<<<<< HEAD
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
=======

    for row in data_list:
        name = row.get("Name", "Unnamed")
        email = row.get("Email")

        try:
            cert_path = os.path.join(OUTPUT_DIR, f"{name}.png")

            if not os.path.exists(cert_path):
                error_msg = f"Certificate not found for {name}"
                print(f"⚠️ {error_msg}")
                error_logs.append(error_msg)
                continue

            print(f"📧 Sending email to {email}...")
>>>>>>> 6ff748039b0b480fb153db4de088e71996bfba7f

            msg = EmailMessage()
            msg["From"] = sender_email
            msg["To"] = email
<<<<<<< HEAD
            msg["Subject"] = "You're In! Welcome to the PORT:80 Crew!"
            msg.set_content(f"Hi {name},\n\nCongratulations and welcome!")
=======
            msg["Subject"] = "Your Certificate"
            msg.set_content("Please find your certificate attached.")
>>>>>>> 6ff748039b0b480fb153db4de088e71996bfba7f

            with open(cert_path, "rb") as f:
                msg.add_attachment(f.read(), maintype="image", subtype="png", filename=f"{name}.png")

            # --- FIX: Use the lock to ensure only one thread sends at a time ---
            with lock:
                server.send_message(msg)
<<<<<<< HEAD
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
=======

            success_msg = f"✅ Email sent successfully to {email}"
            print(success_msg)
            success_logs.append(success_msg)

        except Exception as e:
            error_msg = f"❌ Failed to send to {email}: {e}"
            print(error_msg)
            error_logs.append(error_msg)

    return {"successes": success_logs, "errors": error_logs}
>>>>>>> 6ff748039b0b480fb153db4de088e71996bfba7f
