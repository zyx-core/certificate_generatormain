from PIL import Image, ImageDraw, ImageFont
from email.message import EmailMessage
import smtplib, os
from dotenv import load_dotenv

load_dotenv()
print("✅ certificate_generator module loaded")

OUTPUT_DIR = "generated_certificates"
os.makedirs(OUTPUT_DIR, exist_ok=True)

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
    for row in data_list:
        try:
            name = row.get("Name", "Unnamed")
            file_name = f"{name}_preview.png" if is_preview else f"{name}.png"
            cert_path = os.path.join(OUTPUT_DIR, file_name)

            abs_cert_path = os.path.abspath(cert_path)
            print(f"📄 Saving certificate to: {abs_cert_path}")

            draw_certificate(template_path, cert_path, row, placeholders)
            print(f"✅ Saved: {cert_path}")

            if is_preview:
                generated_path = cert_path
                break

        except Exception as e:
            print(f"❌ ERROR generating for {row.get('Name', 'Unknown')}: {e}")
            errors.append(f"{row.get('Name', 'Unknown')}: {str(e)}")

    return generated_path if is_preview else errors

def send_certificates_only(data_list):
    """Sends certificates and returns a log of successes and errors."""
    smtp_host = os.getenv("EMAIL_HOST")
    smtp_port = int(os.getenv("EMAIL_PORT", 587))
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")

    success_logs = []
    error_logs = []

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

            msg = EmailMessage()
            msg["From"] = sender_email
            msg["To"] = email
            msg["Subject"] = "Your Certificate"
            msg.set_content("Please find your certificate attached.")

            with open(cert_path, "rb") as f:
                msg.add_attachment(f.read(), maintype="image", subtype="png", filename=f"{name}.png")

            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)

            success_msg = f"✅ Email sent successfully to {email}"
            print(success_msg)
            success_logs.append(success_msg)

        except Exception as e:
            error_msg = f"❌ Failed to send to {email}: {e}"
            print(error_msg)
            error_logs.append(error_msg)

    return {"successes": success_logs, "errors": error_logs}
