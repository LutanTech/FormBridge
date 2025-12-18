import random
from datetime import datetime, timedelta
import string, secrets, uuid, base64, json, hmac, hashlib, requests
from flask_mail import Mail, Message
from sqlalchemy import column


def send_devices_limit_email(mail, user_email, link, username=None):
    try:
        plain_body = (
            f"Hello,\n\n"
            f"Your link for FormBridge is: {link}\n"
            f"Please use this to set the new device limit. This link expires in 3 minutes.\n\n"
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
                        <p style="margin:0 0 18px;">Hello {username if username else ''}, use the link below to verify your account and change your devices limit.</p>
                        <div style="background:rgba(255,255,255,0.2); padding:16px; border-radius:8px; margin-bottom:18px; font-size:12px; font-weight:700;">
                           <a href="{link}">Confirm</a> or paste in your browser this link \n
                           {link}
                        </div>
                        <p style="margin:0; font-size:13px; opacity:0.85; color:white;">This OTP will expire in 3 minutes.<br>-- FormBridge --</p>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        msg = Message(
            subject="Formbridge : Set New Device Limit ",
            recipients=[user_email],
            body=plain_body,
            html=html_body
        )

        mail.send(msg)
        print(f"Link sent to {user_email}")

    except Exception as e:
       print(f"[400] Email send failed: {e}")
       
       
def generate_temp_link(user_id, expiry_seconds=180):
    payload = {
        "id": user_id,
        "exp": (datetime.utcnow() + timedelta(seconds=expiry_seconds)).timestamp()
    }
    payload_str = json.dumps(payload)
    sig = hmac.new("not_really_a_secret".encode(), payload_str.encode(), hashlib.sha256).hexdigest()
    token = base64.urlsafe_b64encode(f"{payload_str}::{sig}".encode()).decode()
    return token

def verify_temp_link(token):
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
