import random
from datetime import datetime, timedelta
import string, secrets, uuid, base64, json, hmac, hashlib, requests
from flask_mail import Mail, Message
from sqlalchemy import column
from flask import request

def generate_account_id(length=7):
    characters = string.digits + string.ascii_uppercase
    return ''.join(random.choice(characters) for _ in range(length)) 

def generate_random_id(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_otp(length=5):
    characters =  string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def decode(data):
    try:
        decoded_bytes = base64.urlsafe_b64decode(data + "===")  
        decoded_str = decoded_bytes.decode("utf-8")
        return json.loads(decoded_str)
    except Exception:
        return False

def encode(data):
    try:
        json_str = json.dumps(data)
        encoded_bytes = base64.urlsafe_b64encode(json_str.encode("utf-8"))
        encoded_str = encoded_bytes.decode("utf-8")
        return encoded_str
    except Exception as e:
        print("Encode error:", e)
        return False


def generate_token(user_id):
    payload = {
        "id": user_id,
        "exp": (datetime.utcnow() + timedelta(hours=720)).timestamp()
    }
    payload_str = json.dumps(payload)
    sig = hmac.new("not_really_a_secret".encode(), payload_str.encode(), hashlib.sha256).hexdigest()
    token = base64.urlsafe_b64encode(f"{payload_str}::{sig}".encode()).decode()
    return token

def validate_token(token, expected_id):
    try:
        decoded = base64.urlsafe_b64decode(token.encode()).decode()
        payload_str, sig = decoded.split("::")
        expected_sig = hmac.new("not_really_a_secret".encode(),
                                payload_str.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            return False
        data = json.loads(payload_str)
        if data["id"] != expected_id:
            return False
        if datetime.utcnow().timestamp() > data["exp"]:
            return False
        return True
    except Exception:
        return False
    
    
def send_otp_email(mail, user_email, otp_code, username=None):
    try:
        plain_body = (
            f"Hello,\n\n"
            f"Your OTP code for FormBridge is: {otp_code}\n"
            f"Please use this to complete your login or registration.\n\n"
            f"FormBridge Team"
        )

        html_body = f"""
        <!doctype html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width,initial-scale=1">
        </head>
        <body style="font-family: system-ui; margin:0; padding:0; background:#f4f6fb;">
            <table width="100%" style="max-width:600px; margin:24px auto; background:#0ea5e9; border-radius:12px; color:#fff;">
                <tr>
                    <td style="padding:28px; text-align:center;">
                        <h1 style="margin:0 0 8px;">Your OTP Code</h1>
                        <p style="margin:0 0 18px;">Hello {username if username else ''}, use the code below to verify your account.</p>
                        <div style="background:rgba(255,255,255,0.2); padding:16px; border-radius:8px; margin-bottom:18px; font-size:24px; font-weight:700;">
                            {otp_code}
                        </div>
                        <p style="margin:0; font-size:12px; opacity:1; color:#0f0;">or click this link to verify. <a href="https://formbridge.vercel.app/verify_email/?email={encode(user_email)}&otp={encode(otp_code)}">Verify</a><br></p>
                        <p style="margin:0; font-size:13px; opacity:0.85; color:white;">This OTP will expire in 3 minutes.<br>-- FormBridge --</p>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        msg = Message(
            subject="Your OTP Code for FormBridge",
            recipients=[user_email],
            body=plain_body,
            html=html_body
        )

        mail.send(msg)
        print(f"OTP sent to {user_email}")

    except Exception as e:
       print(f"[400] Email send failed: {e}")
       
       
import json
from fpdf import FPDF

# ---- FORM INPUT DECODER ----
def decode_form_inputs(raw_inputs):
    """
    raw_inputs: str (JSON string like '["-name", "adm", "phone"]')
    Returns list of dicts with keys '-name' and 'label'
    """
    try:
        inputs = json.loads(raw_inputs)
    except Exception as e:
        print("Failed to decode form inputs:", e)
        return []

    cleaned = []
    for item in inputs:
        if isinstance(item, str):
            # convert "-name" -> "name" for safe attribute access
            fname = item.lstrip("-")
            label = fname.capitalize() if fname else None
            if fname:
                cleaned.append({"-name": fname, "label": label})
    return cleaned


# ---- PDF CREATOR ----
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        if hasattr(self, 'header_text'):
            self.set_font("Arial", "B", 14)
            self.cell(0, 10, self.header_text, ln=True, align="C")
            self.ln(4)

    def footer(self):
        if hasattr(self, 'footer_text'):
            self.set_y(-15)
            self.set_font("Arial", "I", 10)
            self.cell(0, 10, self.footer_text, 0, 0, "C")

from fpdf import FPDF
def make_pdf_all(header_text, footer_text, form, submissions):
    import json
    from fpdf import FPDF

    # Decode inputs
    try:
        form_inputs = json.loads(form.inputs)
    except Exception:
        form_inputs = []

    # Prepare columns
    columns = []
    for inp in form_inputs:
        if isinstance(inp, str):
            fname = inp.replace("-", "")
            columns.append((fname, fname.upper()))
    columns = [("row", "#")] + columns

    # Orientation
    pdf_orientation = 'L' if len(columns) > 6 else 'P'
    pdf = FPDF(orientation=pdf_orientation)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Header
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 12, header_text, ln=True, align="C")
    pdf.ln(6)

    # Page width
    page_width = pdf.w - 2 * pdf.l_margin

    # Minimal widths
    min_col_widths = {
        "row": 8, "adm": 40, "phone": 30, "name": 35, "age": 10, "email": 50,
        "topic": 30, "assignment": 30, "units": 30
    }

    # Compute raw widths
    raw_widths = []
    for fname, label in columns:
        pdf.set_font("Times", "B", 12)
        header_width = pdf.get_string_width(label) + 4

        max_content_width = 0
        for sub in submissions:
            val = getattr(sub, fname, "")
            if fname == "adm" and val:
                val = str(val).upper()
            elif fname == "name" and val:
                val = str(val).title()
            elif fname == "email" and val:
                val = str(val)
            else:
                val = str(val)
            pdf.set_font("Times", "", 10 if fname not in ["email","topic","assignment"] else 9)
            max_content_width = max(max_content_width, pdf.get_string_width(val) + 4)

        min_width = min_col_widths.get(fname, 15)
        raw_widths.append(max(min_width, header_width, max_content_width))

    # Scale to page width
    total_raw_width = sum(raw_widths)
    scale = page_width / total_raw_width
    col_widths = [w * scale for w in raw_widths]

    # Table header
    pdf.set_font("Times", "B", 12)
    pdf.set_fill_color(180, 180, 180)
    x_start = pdf.get_x()
    y_start = pdf.get_y()
    for idx, (_, label) in enumerate(columns):
        pdf.set_xy(x_start + sum(col_widths[:idx]), y_start)
        pdf.multi_cell(col_widths[idx], 8, label, border=1, align='C', fill=True)
    pdf.set_xy(x_start, y_start + 8)

    # Table body
    for i, sub in enumerate(submissions, 1):
        row_values = [str(i)]
        for fname, _ in columns[1:]:
            val = getattr(sub, fname, "")
            if fname == "adm" and val:
                val = str(val).upper()
            elif fname == "name" and val:
                val = str(val).title()
            elif fname == "email" and val:
                val = str(val)
            else:
                val = str(val)
            row_values.append(val)

        fill = i % 2 == 1
        if fill:
            pdf.set_fill_color(240, 240, 240)

        # Max lines per row
        max_lines = 1
        for idx, text in enumerate(row_values):
            font_size = 12 if columns[idx][0] not in ["email","topic","assignment"] else 10
            pdf.set_font("Times", "", font_size)
            if columns[idx][0] in ["adm", "phone", "email"]:
                lines = [text]  # no wrap
            else:
                lines = pdf.multi_cell(col_widths[idx], 6, text, border=0, split_only=True)
            max_lines = max(max_lines, len(lines))

        row_height = max_lines * 6
        y_row_start = pdf.get_y()

        # Draw cells
        for idx, text in enumerate(row_values):
            x_cell = pdf.l_margin + sum(col_widths[:idx])
            cw = col_widths[idx]

            if fill:
                pdf.rect(x_cell, y_row_start, cw, row_height, style='F')
            pdf.rect(x_cell, y_row_start, cw, row_height)

            pdf.set_xy(x_cell + 1, y_row_start + 1)

            # Email blue
            pdf.set_text_color(0, 0, 180 if columns[idx][0]=='email' else 0)

            # Font size shrink
            font_size = 12 if columns[idx][0] not in ["email","topic","assignment"] else 10
            pdf.set_font("Times", "", font_size)
            if columns[idx][0] in ["adm","phone","email"]:
                # shrink if needed
                while pdf.get_string_width(text) > (cw-2) and font_size > 6:
                    font_size -= 1
                    pdf.set_font("Times", "", font_size)
                pdf.cell(cw-2, 6, text)
            else:
                pdf.multi_cell(cw-2, 6, text)

        pdf.set_y(y_row_start + row_height)

    # Footer
    pdf.set_text_color(0, 0, 0)
    pdf.ln(6)
    pdf.set_font("Times", "I", 10)
    pdf.cell(0, 12, footer_text, align="C")

    out = f"{form.name_str}_submissions.pdf"
    pdf.output(out)
    return out

import pyotp
import qrcode
from io import BytesIO


def generate_2fa_secret():
    raw_secret = pyotp.random_base32()
    return base64.b64encode(raw_secret.encode()).decode()

def get_totp(secret_b64):
    raw_secret = base64.b64decode(secret_b64).decode()
    return pyotp.TOTP(raw_secret)

def generate_temp_token(user_id, expiry_seconds=300):
    payload = {
        "id": user_id,
        "exp": (datetime.utcnow() + timedelta(seconds=expiry_seconds)).timestamp()
    }
    payload_str = json.dumps(payload)
    sig = hmac.new("not_really_a_secret".encode(), payload_str.encode(), hashlib.sha256).hexdigest()
    token = base64.urlsafe_b64encode(f"{payload_str}::{sig}".encode()).decode()
    return token

def verify_temp_token(token):
    try:
        decoded = base64.urlsafe_b64decode(token.encode()).decode()
        payload_str, sig = decoded.split("::")
        expected_sig = hmac.new("not_really_a_secret".encode(), payload_str.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            return None
        data = json.loads(payload_str)
        if datetime.utcnow().timestamp() > data["exp"]:
            return None
        return data["id"]
    except Exception:
        return None

def get_client_ip():
    return (
        request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        or request.headers.get("X-Real-IP")
        or request.remote_addr
    )
