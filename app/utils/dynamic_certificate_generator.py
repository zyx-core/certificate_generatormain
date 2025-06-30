from PIL import Image, ImageDraw, ImageFont
import os, zipfile

def generate_certificates(data, template_path, config):
    output_dir = "generated_certificates"
    os.makedirs(output_dir, exist_ok=True)

    template = Image.open(template_path)

    for row in data:
        cert = template.copy()
        draw = ImageDraw.Draw(cert)

        for item in config:
            key = item.get("key")
            x = item.get("x", 0)
            y = item.get("y", 0)
            font_size = item.get("font_size", 40)
            color = item.get("color", "black")

            value = str(row.get(key, "")).strip()
            if not value:
                continue

            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                font = ImageFont.load_default()

            draw.text((x, y), value, fill=color, font=font)

        filename = f"{row.get('name', 'unknown')}.png"
        cert_path = os.path.join(output_dir, filename)
        cert.save(cert_path)

    zip_path = "certificates.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            if os.path.isfile(file_path):
                zipf.write(file_path, arcname=filename)

    return zip_path
