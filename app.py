from flask import Flask, jsonify, request, send_file, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

from utils import generate_random_id, decode, generate_otp, encode, generate_token, validate_token, send_otp_email, make_pdf_all, get_totp, generate_2fa_secret, generate_temp_token, verify_temp_token, get_client_ip

from emails import send_devices_limit_email, generate_temp_link, verify_temp_link, send_qr_email

from flask_mail import Mail
from datetime import datetime, timedelta
from flask_migrate import Migrate
import models
from models import User, Log, Help, Form, Submission, Device
import pyotp, base64
import qrcode
from io import BytesIO

app = Flask(__name__)

app.config['SECRET_KEY'] = 'not_really_a_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///host.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'lutancorpinfoteam@gmail.com'
app.config['MAIL_PASSWORD'] = 'ecpb aukn nagd csqh'
app.config['MAIL_DEFAULT_SENDER'] = ('FormBridge', 'lutancorpinfoteam@gmail.com')
app.config['ADMIN_EMAIL'] = 'lutancorpinfoteam@gmail.com'

ALLOWED_FRONTEND_ORIGINS = [
     "http://127.0.0.1:5500",
    "https://formbridge.vercel.app"
]

# CORS(app, origins=ALLOWED_FRONTEND_ORIGINS, supports_credentials=True)
CORS(app)
models.db.init_app(app)
db = models.db
migrate = Migrate(app, db)
mail = Mail(app)


from flask import request
import json
import user_agents

def log(content, type):
    try:
        # IP
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)

        ua_string = request.headers.get('User-Agent', '')
        ua = user_agents.parse(ua_string)

        meta = {
            "ip": ip,
            "device_type": "Mobile" if ua.is_mobile else "Tablet" if ua.is_tablet else "PC",
            "device_model": ua.device.model or "Unknown",
            "device_brand": ua.device.brand or "Unknown",
            "os": ua.os.family or "Unknown",
            "browser": ua.browser.family or "Unknown",
        }

        meta_json = json.dumps(meta)

        new_log = Log(
            id=generate_random_id(6),

            type=type,
            content=content,
            requestor=meta_json
        )

        db.session.add(new_log)
        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        print("error during logging", e)
        return False



@app.route('/')
def index():
    return '[500] Invalid response received from server'


@app.route('/register', methods=['POST'])
def register():
    raw = request.get_json()

    encoded = raw.get("data")

    safe = decode(encoded)

    if not safe:
        log('[400] Failed to decode in /register route', 'error')
        return jsonify({'error': 'An error occured on our end. Please try again'}), 400

    try:
        username = safe.get('username')
        email = safe.get('email')
        password = safe.get('password')

        exists = User.query.filter_by(username=username).first()
        e_exists = User.query.filter_by(email=email).first()

        if exists:
            return jsonify({'error': 'Username already in use. Please choose another one'}), 400

        if e_exists:
            return jsonify({'error': 'Email already exists. Please login'}), 400

        new_user = User(
            username=username,
            email=email )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        try:
           send_otp_email(mail, new_user.email, generate_otp(5))
           log(f'[200] New User joined : {new_user.username}', 'success')
           return jsonify({'msg': 'Registered successfully. Check your email for OTP'}), 200
        except Exception as e:
            log(f'Failed to send OTP to {new_user.email}: {str(e)}', 'error')
            return jsonify({'error':'Failed to send otp. Please retry again'}), 400
    except Exception as e:
        db.session.rollback()
        log(f'[500] Database error in /register route: {str(e)}', 'error')
        return jsonify({'error': 'Failed to register. Contact Support'}), 500

@app.route("/login", methods=['POST'])
def login():
    raw = request.get_json()
    encoded = raw.get("data")
    data = decode(encoded)

    if not data:
        log('[400] Failed to decode in /login route', 'error')
        return jsonify(encode({'error': 'An error occurred. Please try again'})), 400

    device = data.get('ua')
    if not device:
        return jsonify({'error':'failed to initiate login. Please disable any extensions.'}), 401
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify(encode({'error': 'Missing login credentials'})), 401

    user = User.query.filter(
        (User.username == username) | (User.email == username)
    ).first()

    if not user:
        return jsonify(encode({'error': 'User not found'})), 401

    if not user.check_password(password):
        return jsonify(encode({'error': 'Invalid password'})), 401

    # If 2FA is enabled
    if user.twofa_secret:
        temp_token = generate_temp_token(user.id)
        return jsonify(encode({
            'required': True,
            'tt': temp_token,
            'info': 'Enter your 2FA code'
        })), 200
    ua = request.headers.get("User-Agent")
    ip = get_client_ip()
    
    try:
        ok, error = check_device(device if device else ua, user.id, ip)
        if not ok:
            return jsonify(encode({"error": f'Failed to login Key Error: {error}'})), 400
        
        return jsonify(encode({ 
              'user': encode(user.to_dict()),
              'expiry': (datetime.utcnow() + timedelta(hours=171)).isoformat(),
              'token': generate_token(user.id)
              })), 200

    except Exception as e:
        log(f'[400] Unknown error in /check_device route : {str(e)}','error')
        return jsonify({'error':f'Please try again: {str(e)}'}), 400
    


def check_device(ua, user_id, ip):
    if not ua or not user_id or not ip:
        return False, "Invalid device, user, or IP"

    now = datetime.utcnow() + timedelta(hours=3)

    device = Device.query.filter_by(
        user_id=user_id,
        ua=ua
    ).first()

    if device:
        # device.last_login = now
        # device.ip = ip 
        try:
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            log(f"[500] Failed updating device: {str(e)}", "error")
            return False, "Database error"

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return False, "User not found"

    max_devices = int(user.devices) if user.devices else 1

    device_count = Device.query.filter_by(user_id=user_id).count()
    if device_count >= max_devices:
        return False, "Maximum number of devices reached"

    new_device = Device(
        user_id=user_id,
        ua=ua,
        ip=ip,
        last_login=now
    )

    try:
        db.session.add(new_device)
        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        log(f"[500] Failed adding device: {str(e)}", "error")
        return False, "Database error"


          
    
@app.route('/login/two_fa', methods=['POST'])
def two_fa_login():

    raw = request.get_json()
    encoded = raw.get("data")
    data = decode(encoded)
    temp_token = data.get('tt')
    otp = data.get('otp')
    device = data.get('ua')
    if not temp_token or not otp or not device:
        return jsonify({"error": "Invalid payload. Please try again"}), 400
    
    user_id = verify_temp_token(temp_token)
    if not user_id:
        return jsonify({"error": "Invalid or expired token"}), 401

    user = User.query.get(user_id)
    if not user or not user.twofa_secret:
        return jsonify({"error": "2FA not set for user"}), 401

    decoded_secret = base64.b64decode(user.twofa_secret).decode()
    totp = pyotp.TOTP(decoded_secret)

    if not totp.verify(otp, valid_window=1):
        return jsonify({"error": "Invalid 2FA code"}), 401
    
    ua = request.headers.get("User-Agent")
    ip = get_client_ip()
    

    try:
        ok, error = check_device(device, user_id, ip)
        if not ok:
            return jsonify(encode({"error": f'Failed to login Key Error: {error}'})), 400

        return jsonify(encode({
                'user': encode(user.to_dict()),
                'expiry': (datetime.utcnow() + timedelta(hours=171)).isoformat(),
                'token': generate_token(user.id)
            })), 200
    
    except Exception as e:
        log(f'[400] Unknown error in /check_device route : {str(e)}','error')
        return jsonify({'error':f'Please try again: {str(e)}'}), 400


@app.route('/verify', methods=['POST'])
def verify():
    raw = request.get_json()
    encoded = raw.get("data")

    data = decode(encoded)

    if not data:
        log('[400] Failed to decode in /verify route', 'error')
        return jsonify({'error': 'An error occurred. Please try again'}), 400
    email = data.get('email')
    otp = data.get('otp')
    user = User.query.filter_by(email=email).first()
    if user:
        if user.otp == '':
            return jsonify({'info':'Already Verified. Please Log in'}), 302

        if otp == user.otp:
            try:
                user.otp = ''
                db.session.commit()
                log(f'[200] user {user.username} verified their email', 'ssuccess')
                return jsonify({'msg':'Account verified sucessfully', 'reload':True}), 200
            except Exception as e:
                db.session.rollback()
                log(f'[500] Database error in /verify route for user {user.username} : {str(e)}', 'error')
                return jsonify({'error':'An error occurred on our end. Please try again'}), 500
        return jsonify({'error':'Incorrect OTP. Please try again or request a new one'}), 401

    return jsonify({'error':'An error occurred. Please request a new otp'}), 400

@app.route('/new_form', methods=['POST'])
def create_new_form():
    raw = request.get_json()
    encoded = raw.get("data")



    data = (encoded)
    if data:
        name = data.get('name')
        deadline_str = data.get('deadline')
        deadline = datetime.fromisoformat(deadline_str)
        desc = data.get('desc')
        ins = data.get('ins')
        selected = data.get('selected') or []
        user_id = data.get('uid')
        token = data.get('token')

        if not user_id or not token:
            return jsonify({'error': 'Missing data in request. Please Login again'}), 404

        user = User.query.filter_by(id=user_id).first()

        if user and validate_token(token, user.id):
            try:
                new_form = Form(
                    name_str=name,
                    user_id=user.id,
                    desc=desc,
                    instructions=ins,
                    inputs=json.dumps(selected),
                    deadline=deadline
                )

                for i in selected:
                    cleaned = i.replace('-', '')
                    setattr(new_form, cleaned, True)

                db.session.add(new_form)
                db.session.commit()

                log(f'[200] New form > {new_form.name} < added by {user.id}', 'ignore')

                return jsonify({'msg': 'Form Created successfully'}), 200

            except Exception as e:
                db.session.rollback()
                log(f'[500] Database error in /new_form route : {str(e)}', 'error')
                return jsonify({'error': 'An unexpected error occured on our end'}), 500

        return jsonify({'error': 'Invalid data received. Please Login again'}), 400

    return jsonify({'error': 'Missing data in request. Please Try again'}), 400

@app.route('/get_forms', methods=['POST'])
def forms_list():
    raw = request.get_json()
    encoded = raw.get("data")

    data = decode(encoded)

    if not data:
        log('[400] Failed to decode in /verify route', 'error')
        return jsonify(encode({'error': 'An error occurred. Please try again'})), 400
    id = data.get('u')
    token = data.get('t')
    device = data.get('d')
    
    if id and token:
        user = User.query.filter_by(id=id).first()
        ua = request.headers.get("User-Agent")
        ip = get_client_ip()
    

        if user:
            ok, error = check_device(device, user.id, ip)
            if not ok:
                return jsonify(encode({"error": f'Failed to login. Key Error: {error}'})), 400
            if validate_token(token, user.id):
                forms = Form.query.filter_by(user_id=id).all()
                
                if forms:
                    data = []
                    for f in forms:
                        subs = Submission.query.filter_by(form_id=f.id).all()
                        sub_count = len(subs)

                        fields = ["name", "age", "phone", "adm", "email", "topic", "assignment", "units"]
                        non_empty_count = 0

                        for s in subs:
                            for field in fields:
                                value = getattr(s, field)
                                if value and str(value).strip() != "":
                                    non_empty_count += 1

                        data.append({
                            **f.to_dict(),
                            "c": sub_count,
                            "n": non_empty_count,
                        })
                            
                    return jsonify(encode({"forms": data,'devices':user.devices })), 200
                return jsonify(encode({"msg": "No forms found. Please add some"})), 404
            return jsonify(encode({'error':'Unauthorized'})), 401
        return jsonify(encode({'error':'Failed to load account. Please reload the page or login again'})), 404
    return jsonify(encode({'error':'Misssing data in request. Please, try again'})), 404

@app.route('/form/<id>')
def get_form(id):
    if id:
        form = Form.query.filter_by(id=id).first()
        if form:
            return jsonify({'form':form.to_v_dict()}), 200
        return jsonify({'error':'Page not found'}), 404
    return jsonify({'error':'Incomplete request'}), 400

@app.route("/form_info", methods=['POST'])
def form_info():
    raw = request.get_json()
    encoded = raw.get("data")
    data = decode(encoded)

    if data:
        fid = data.get('fid')
        uid = data.get('uid')
        token = data.get('token')
        if fid:
            if validate_token(token, uid):
                form = Form.query.filter_by(id=fid, user_id=uid).first()
                if form:
                    count = Submission.query.filter_by(form_id=form.id).count()
                    return jsonify(encode({'submissions': count,'form':form.to_dict(), 'db_id':encode({'u':uid, 'f':fid}), 'token':generate_token(uid)})), 200

                return jsonify({'error':'Form not found'}), 404
            return jsonify({'error':'Unauthorized. Please, login again'}), 401
        return jsonify({'error':'Missing data in request. Please try again'}), 404
    return jsonify({'error':'Missing data in request. Please try again'}), 404

@app.route("/submit", methods=["POST"])
def submit_form():
    try:
        raw = request.get_json()
        encoded = raw.get("data")
        data = decode(encoded)

        if not data:
            return jsonify({"ok": False, "msg": "Invalid payload"}), 400

        form_id = data.get("form_id")
        user_data = data.get("user_data")

        if not form_id:
            return jsonify({"ok": False, "msg": "Missing form or user"}), 400


        # Fetch form
        form = Form.query.filter_by(id=form_id).first()
        if not form:
            return jsonify({"ok": False, "msg": "Form not found"}), 404

        if not form.is_open:
            return jsonify({"ok": False, "msg": "Form is closed"}), 403

        # Parse inputs list
        try:
            fields = json.loads(form.inputs)
        except:
            fields = []

        cleaned = {}
        for f in fields:
            key = f.replace("-", "")  # "-name" becomes "name"
            if key in user_data:
                cleaned[key] = user_data[key]

        # Insert into submissions table
        new_sub = Submission(
            form_id=form.id,
            instructor=form.user_id,
            name=cleaned.get("name"),
            age=cleaned.get("age"),
            phone=cleaned.get("phone"),
            adm=cleaned.get("adm"),
            email=cleaned.get("email"),
            topic=cleaned.get("topic"),
            assignment=cleaned.get("assignment"),
            units=cleaned.get("units")
        )


        db.session.add(new_sub)
        db.session.commit()

        return jsonify({
            "ok": True,
            "msg": "Submitted successfully",
            "saved": cleaned
        })

    except Exception as e:
        log(f"[500] Database error in /submit route:  {str(e)}")
        return jsonify({"ok": False, "msg": "Server error"}), 500
    
@app.route('/toggle_db', methods=['POST'])
def toggle():
        raw = request.get_json()
        encoded = raw.get("data")
        data = decode(encoded)

        if not data:
            return jsonify({"ok": False, "msg": "Invalid payload"}), 400

        form_id = data.get("f")
        id = data.get('u')
        token = data.get('t')
        user = User.query.filter_by(id=id).first()
        
        if not user or not validate_token(token, user.id):
            return jsonify({'error':'Unauthorized. Please ogin again'}), 401
        
            
        form = Form.query.filter_by(id=form_id).first()
        
        if not form:
            return jsonify({"ok": False, "msg": "Database not found"}), 404
        
        if user.id != form.user_id:
            return jsonify({"ok": False, "msg": "Unauthorized"}), 401

        if not form.is_open:
            form.is_open = True
            db.session.commit()
            return jsonify({"ok": True, "msg": "Database opened"}), 200
        form.is_open = False
        db.session.commit()
        return jsonify({"ok": True, "msg": "Database Locked"}), 200
        

@app.route('/delete_form', methods=['POST'])
def delete_form():
    raw = request.get_json()
    encoded = raw.get("data")
    data = decode(encoded)

    id = data.get('uid')
    fid = data.get('fid')
    token = data.get('token')

    if fid and id and token:
            user = User.query.filter_by(id=id).first()
            if user and validate_token(token, user.id):
                form = Form.query.filter_by(id=fid).first()
                if form:
                    try:
                        db.session.delete(form)
                        db.session.commit()
                        return jsonify({'msg':'Form deleted  successfully'}), 200
                    except Exception as e:
                        db.session.rollback()
                        log(f'[500] Database error in /delete route: {str(e)}', 'error')
                        return jsonify({'error':'Failed to delete : Database error'}), 500
                return jsonify({'error':'Form not found'}), 404
            return jsonify({'error':'Unauthorized action. Please login again'}), 401
    return jsonify({'error':'Missing data in request'}), 404


@app.route('/database/<data>')
def database(data):
    try:
        limit = int(request.args.get('limit') or 50)
        page = int(request.args.get('page') or 1)
    except ValueError:
        return jsonify({'error': 'Invalid limit or page'}), 400

    data = decode(data)
    uid = data.get('u')
    fid = data.get('f')
    token = data.get('t')

    if not (uid and fid and token):
        return jsonify({'error': 'Missing data in request'}), 404

    user = User.query.filter_by(id=uid).first()
    if not user or not validate_token(token, user.id):
        return jsonify({'error': 'Unauthorized. Please login again'}), 401

    form = Form.query.filter_by(id=fid, user_id=user.id).first()
    if not form:
        return jsonify({'error': 'Database not found'}), 404

    query = Submission.query.filter_by(form_id=form.id, instructor=user.id)
    total = query.count()
    submissions = query.offset((page - 1) * limit).limit(limit).all()

    has_next = (page * limit) < total

    return jsonify({
        'submissions': [s.to_dict() for s in submissions],
        'code': 200,
        'inputs': json.loads(form.inputs),
        'db': encode(form.name_str),
        'page': page,
        'limit': limit,
        'total': total,
        'has_next': has_next
    }), 200

@app.route('/delete_submission', methods=['POST'])
def delete_sub():
    raw = request.get_json()
    encoded = raw.get("data")
    data = decode(encoded)
    if data:
        i = data.get('i')
        user_data = decode(i)
        uid = user_data.get('u')
        t = user_data.get('t')
        s_id = data.get('sid')
        user = User.query.filter_by(id=uid).first()
        if user and validate_token(t, user.id):
            submission = Submission.query.filter_by(id=s_id, instructor=uid).first()
            if submission:
                try:
                    db.session.delete(submission)
                    db.session.commit()
                    return jsonify({'msg':'Submission deleted successfully'}), 200
                except Exception as e:
                    db.session.rollback()
                    log(f'[500] Database error in /delete submission route: {str(e)}')
                    return jsonify({'error':'Failed to delete submission.Key error:Database'}), 500
            return jsonify({'error':'Submission not found'}), 400
        return jsonify({'Unauthorized. Please Login again'}), 401

@app.route('/edit_submission', methods=['POST'])
def edit_sub():
    raw = request.get_json()
    encoded = raw.get("data")
    data = decode(encoded)

    if not data:
        return jsonify({'error': 'Invalid payload'}), 400

    print(data)

    i = data.get('i')
    user_data = decode(i) if i else {}

    uid = user_data.get('u')
    t = user_data.get('t')
    s_id = data.get('sid')
    fields = data.get('updated')
    print(uid, t, s_id)

    if not uid or not t or not s_id:
        return jsonify({'error': 'Missing parameters'}), 400

    user = User.query.filter_by(id=uid).first()

    if not (user and validate_token(t, user.id)):
        return jsonify({'error': 'Unauthorized. Please login again'}), 401

    submission = Submission.query.filter_by(id=s_id, instructor=uid).first()

    if not submission:
        return jsonify({'error': 'Submission not found'}), 400

    protected = {'id', 'form_id', 'instructor', 'at'}

    try:
        for key, value in fields.items():
            if hasattr(submission, key) and key not in protected:
                setattr(submission, key, value)

        db.session.commit()
        return jsonify({'msg': 'Submission updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        log(f'[500] Database error in /edit_submission route: {str(e)}', 'error')
        return jsonify({'error': 'Failed to update submission'}), 500

@app.route("/print", methods=["POST"])
def print_all():
    raw = request.get_json()
    enc = raw.get("data")
    data = decode(enc)

    if not data:
        return jsonify({"error": "Invalid payload"}), 400

    i = decode(data.get('i'))

    fid = i.get("f")
    header = data.get("header", "")
    footer = data.get("footer", "")

    form = Form.query.filter_by(id=fid).first()
    if not form:
        return jsonify({"error": "Form not found"}), 404

    submissions = Submission.query.filter_by(form_id=fid).all()
    print(submissions)

    pdf_path = make_pdf_all(header, footer, form, submissions)

    return send_file(pdf_path, as_attachment=True)

@app.route('/refresh/db')
def refresh():
    try:
        newTest = Form(user_id='Test')
        db.session.add(newTest)
        return jsonify({'msg':'Refreshed database successfully'}), 200
    except Exception as e:
        log(f'[500] error in /refresh/db route: {e}', 'error')
        return jsonify({'error':f'Failed.Please, try again'}), 500

#2FA==============

@app.route('/activate_two_fa', methods=['POST'])
def activate_two_fa():
    raw = request.get_json()
    enc = raw.get("data")
    data = decode(enc)

    if not data:
        return jsonify({"error": "Invalid payload"}), 400

    user_data = decode(data.get('u'))
    if not user_data:
        return jsonify({"error": "Invalid user data"}), 400

    uid = user_data.get("id")   
    token = data.get("token") 
    user = User.query.filter_by(id=uid).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.twofa_secret:
        return jsonify({'error': '2FA already active'}), 401

    if not validate_token(token, uid):
        return jsonify({'error':'Unauthorized. Please login again'}), 401

    try:
        # Generate 2FA secret
        user.twofa_secret = generate_2fa_secret()
        db.session.commit()

        # Generate QR code as base64
        totp = get_totp(user.twofa_secret)
        account_name = getattr(user, 'name', None) or user.username or user.email
        uri = totp.provisioning_uri(name=account_name, issuer_name="FormBridge")

        qr_img = qrcode.make(uri)
        buf = BytesIO()
        qr_img.save(buf, format='PNG')
        buf.seek(0)
        qr_b64 = base64.b64encode(buf.getvalue()).decode()

        return jsonify({
            'message': '2FA activated successfully',
            'account_name': account_name,
            'qr_code_base64': qr_b64,
            'key': user.twofa_secret 
            
        }), 200

    except Exception as e:
        log(f'[500] Database error occurred in /activate_two_fa route: {str(e)}')
        return jsonify({'error':'An internal error occurred'}), 500

@app.route('/check2fa/<user>')
def check_2fa(user):
    if user:
        decoded = decode(user)
        if decoded:
            stored = User.query.filter_by(id=decoded.get('id')).first()
            if stored:
                if stored.twofa_secret:
                    return jsonify({'success':True}), 200
                return jsonify({'success':False}), 200
            return jsonify({'error':'User not found'}), 404
        return jsonify({'error':'An error occurred'}), 400
    return jsonify({'error':'Invalid payload received'}), 502


@app.route('/resend_qr/<payload>')
def resend_qr(payload):
    try:
        data = decode(payload)
        user = decode(data.get('u'))
        uid = user.get('id')
        token = data.get('t')
        user = User.query.filter_by(id=uid).first()
        if user and validate_token(token, uid):
            user.twofa_secret = generate_2fa_secret()
            db.session.commit()

            totp = get_totp(user.twofa_secret)
            account_name = getattr(user, 'name', None) or user.username or user.email
            uri = totp.provisioning_uri(name=account_name, issuer_name="FormBridge")

            qr_img = qrcode.make(uri)
            buf = BytesIO()
            qr_img.save(buf, format='PNG')
            buf.seek(0)
            qr_b64 = base64.b64encode(buf.getvalue()).decode()
            img = qr_b64
            key = user.twofa_secret

            try:
                send_qr_email(mail, user.email, img, key, user.username)
                return jsonify({'msg':'QR Code send to your Email. Please open your mail app to scan the QR or enter the key in your authenticator app'}), 200
            except Exception as e:
                log(f'[400] Unexpected error in send_qr_email // for user :( {user.email} ): {str(e)}', 'error')
    except Exception as e:
        log(f'[400] Unexpected error in send_qr_email // for user :( {user.email} ): {str(e)}', 'error')
            

@app.route('/get_devices', methods=['POST'])
def devices():
    raw = request.get_json()
    enc = raw.get("data")
    data = decode(enc)

    if not data:
        return jsonify({"error": "Invalid payload"}), 400

    u = decode(data.get('u'))
    token = data.get('t')
    if u and token:
        if validate_token(token, u.get('id')):
            user = User.query.filter_by(id= u.get('id')).first()
            if user:
               devices  = Device.query.filter_by(user_id=user.id).all()
               return jsonify(encode({'devices':[d.to_dict() for d in devices]})), 200
            return jsonify({'error':'User not found'}), 404
        return jsonify({'error':'unauthorized. please, login'}), 401
    return  jsonify({'error':'Invalid payload. Please login again'}), 400

@app.route('/logout', methods=['POST'])
def logout():
    
    raw_data = request.get_json()
    data = decode(raw_data.get('data'))
    print(data)
    token = data.get('t')
    user_data = decode(data.get('u'))
    print(user_data)
    
    id = user_data.get('id')
    device_ua = data.get('d')
    
    if data and id:
        user = User.query.filter_by(id=id).first()
        if user:
            if validate_token(token, user.id):
                device = Device.query.filter_by(ua=device_ua).first()
                if device:
                    if device.user_id == user.id:
                        db.session.delete(device)
                        db.session.commit()
                        return jsonify({'msg':'Logged out'}), 200
                    return jsonify({'error':'Unauthorized action'}),401
                return jsonify({'msg':'Already Logged out'}), 200
            return jsonify({'error':'Unauthorized action'}),401
        return jsonify({'error':'Logout error. Key Error : User'}), 400
    return jsonify({'error':'Logout error : Invalid'}), 400

@app.route('/change_devices_limit/<user_id>/<token>/<int:val>')
def change_limit(user_id, token, val):
    if user_id and token and val:
        user = User.query.filter_by(id=user_id).first()
        print(user_id)
        if user:
            temp_link = generate_temp_link(user.id)
            payload = {
                'l':temp_link,
                'v':val
            }
            try:
                link = f'http://127.0.0.1:5500/devices/?p={encode(payload)}'
                send_devices_limit_email(mail, user.email, link, user.username)
                return jsonify({'msg':'Link send to your Email. Please open your mail app and click to verify'}), 200
            except Exception as e:
                log(f'[400] Unexpected error in send_device_limit_email // change devie limit for user :( {user.email} ): {str(e)}', 'error')
        return jsonify({'error':'Failed to change. Please retry'}), 400
    return jsonify({'error':'Invalid payload received'}), 400

@app.route('/activate_limit/<raw>')
def activate_limit(raw):
    if raw:
        payload = decode(raw)
        if payload:
            link = payload.get('l')
            val = payload.get('v')
            if link and val:
                if verify_temp_link(link):
                    decoded = base64.urlsafe_b64decode(link.encode()).decode()
                    if decoded:
                        decoded_str, sig = decoded.split('::')
                        uid  = json.loads(decoded_str).get('id')
                        if uid:
                            user = User.query.filter_by(id=uid).first()
                            if user:
                                try:
                                    user.devices = int(val)
                                    db.session.commit()
                                    return jsonify({'msg':f'Updated devices limit to {val} successfully'}), 200
                                except Exception  as e:
                                    log(f'[500] Database error in /activate limit route: {str(e)}', 'error')
                                    return jsonify({'error':f'Database error : {str(e)}'}), 500
                            return jsonify({'error':'User not found'}), 404
                        return jsonify({'error':'Invalid payload. Please retry : UID'}), 400
                    return jsonify({'error':'Invalid payload. Please retry : P_STR'}), 400
                return jsonify({'error':'Expired link. Please retry again'}), 401
                
            return jsonify({'error':'Invalid payload. Please retry : V|L'}), 400
        return jsonify({'error':'Invalid payload. Please retry : P'}), 400
    return jsonify({'error':'Invalid payload. Please retry : R'}), 400


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print('app.run(debug=True, port=6050, host="0.0.0.0")')
    app.run(debug=True, port=6050, host="0.0.0.0")

