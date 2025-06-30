from PIL import Image, ImageDraw, ImageFont
from email.message import EmailMessage
import smtplib, os
from dotenv import load_dotenv



load_dotenv()
def generate_and_send_dynamic(data, template_path, placeholders: dict):
    from PIL import Image, ImageDraw, ImageFont
    import os, smtplib
    from email.message import EmailMessage
    from dotenv import load_dotenv

    load_dotenv()
    output_dir = "generated_certificates"
    os.makedirs(output_dir, exist_ok=True)

    smtp_host = os.getenv("EMAIL_HOST")
    smtp_port = int(os.getenv("EMAIL_PORT"))
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")

    template = Image.open(template_path)
    font = ImageFont.truetype("arial.ttf", 60)
    errors = []

    for row in data:
        name = row.get("Name")
        email = row.get("Email")
        cert = template.copy()
        draw = ImageDraw.Draw(cert)

        for field, pos in placeholders.items():
            value = str(row.get(field, ""))
            draw.text(tuple(pos), value, fill="black", font=font)

        cert_path = os.path.join(output_dir, f"{name}.png")
        cert.save(cert_path)

        try:
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

        except Exception as e:
            errors.append(f"{email}: {e}")

    return errors
