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
            <table width="100%" style="max-width:600px; margin:24px auto; background:#000; border-radius:12px; color:#fff;">
                <tr>
                    <td style="padding:28px; text-align:center;">
                        <h1 style="margin:0 0 8px;">Set New Device Limit</h1>
                        <p style="margin:0 0 18px;">Hello {username if username else ''}, use the link below to verify your account and change your devices limit.</p>
                        <div style="background:rgba(255,255,255,0.2); padding:16px; border-radius:8px; margin-bottom:18px; font-size:12px; font-weight:700;">
                           <a style="padding:10px 20px; color:#000; width:150px; margin-bottom:50px; border-radius:20px; background:#0f0" href="{link}">Confirm</a> <br> or paste in your browser this link <br> <hr style="width:100%">
                          <a style="color:#0f0" href="{link}">{link}</a>
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
       
       
def generate_temp_link(user_id, expiry_seconds=1800):
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

import base64
from io import BytesIO

def format_key(key, group_size=4):
    key = key.replace(" ", "")
    return ' '.join(key[i:i+group_size] for i in range(0, len(key), group_size))


def send_qr_email(mail, user_email, img, key, username=None):
    try:
        decoded_key = base64.b64decode(key).decode("utf-8")
        formatted_key = format_key(decoded_key, 4)

        plain_body = (
            f"Hello, {username}\n\n"
            f"Your key for FormBridge 2FA activation is: {decoded_key}\n"
            f"Please enter this key in your authenticator app. This QR expires in 3 minutes.\n\n"
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
            <table width="100%" style="max-width:600px; margin:24px auto; background:#000; border-radius:12px; color:#fff;">
                <tr>
                    <td style="padding:28px; text-align:center;">
                        <h1>Activate Two Factor Authentication</h1>
                        <p>
                            Hello {username or ''}, scan this QR code using your authenticator app
                            or enter the secret key manually.
                        </p>

                        <div style="background:rgba(255,255,255,0.2); padding:16px; border-radius:8px; margin:18px 0; font-size:25px; font-weight:700;">
                            {formatted_key}
                        </div>

                        <p style="font-size:13px; opacity:0.85;">
                            This QR will expire in 3 minutes.<br>
                            FormBridge
                        </p>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        msg = Message(
            subject="FormBridge : Activate 2FA",
            recipients=[user_email],
            body=plain_body,
            html=html_body
        )
        img_base64 = img
        
        img_bytes = BytesIO(base64.b64decode(img_base64))
        msg.attach("qr.png", "image/png", img_bytes.read())
        mail.send(msg)
        print(f"Link sent to {user_email}")

    except Exception as e:
        print(f"[400] Email send failed: {e}")

def send_reset_password_otp(mail, user_email, otp, username=None):
    try:

        plain_body = (
            f"Hello, {username}\n\n"
            f"Your FormBridge reset password OTP is: {otp}\n"
            f"Please enter this OTP to enable you to reset your password.\n\n"
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
            <table width="100%" style="max-width:600px; margin:24px auto; background:#000; border-radius:12px; color:#fff;">
                <tr>
                    <td style="padding:28px; text-align:center;">
                        <h1>Reset Password OTP</h1>
                        <p>
                            Hello {username or ''}, use this OTP to reset your password. If you did not request this OTP, please contact us <a href="https://formbridge.vercel.app/support">here</a>.
                        </p>

                        <div style="background:rgba(255,255,255,0.2); padding:16px; border-radius:8px; margin:18px 0; font-size:25px; font-weight:700;">
                            {otp}
                        </div>

                        <p style="font-size:13px; opacity:0.85;">
                            This OTP will expire in 24 Hours<br>
                            FormBridge
                        </p>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        msg = Message(
            subject="FormBridge : Reset Password",
            recipients=[user_email],
            body=plain_body,
            html=html_body
        )
        mail.send(msg)
        print(f"Link sent to {user_email}")

    except Exception as e:
        print(f"[400] Email send failed: {e}")
