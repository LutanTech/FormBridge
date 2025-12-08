import random
from datetime import datetime, timedelta
import string, secrets, uuid, base64, json, hmac, hashlib, requests
from flask_mail import Mail, Message


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
                        <p style="margin:0; font-size:20px; opacity:1; color:#0f0;">or click this link to verify. <a href="http://127.0.0.1:5500/verify_email/?email={encode(user_email)}&otp={encode(otp_code)}">Verify</a><br></p>
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
       
def decode_form_inputs(raw):
    if not raw:
        return []
    
    arr = json.loads(raw)  # first decode

    cleaned = []
    for item in arr:
        if isinstance(item, str):
            try:
                cleaned.append(json.loads(item))  # second decode
            except:
                pass
        elif isinstance(item, dict):
            cleaned.append(item)

    return cleaned


from fpdf import FPDF
import json
import os

def make_pdf_all(header_text, footer_text, form, submissions):
    form_inputs = decode_form_inputs(form.inputs)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for sub in submissions:
        pdf.add_page()

        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, header_text, ln=True, align="C")

        pdf.ln(4)
        pdf.set_font("Arial", "", 12)

        for inp in form_inputs:
            fname = inp.get("-name")
            label = inp.get("label", fname)
            value = getattr(sub, fname, None)

            if value:
                pdf.multi_cell(0, 8, f"{label}: {value}")

        pdf.ln(6)
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 10, footer_text, align="C")

    out = f"{form.id}_submissions.pdf"
    pdf.output(out)
    return out
