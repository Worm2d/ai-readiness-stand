"""Генерация QR-кодов в base64 data-URI для встраивания прямо в HTML/PDF."""
import base64
from io import BytesIO

import qrcode


def make_qr_data_uri(url: str) -> str:
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"
