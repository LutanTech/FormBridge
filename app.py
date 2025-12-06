from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from utils import generate_random_id, decode, generate_otp, encode, generate_token, validate_token, send_otp_email
from flask_mail import Mail
from datetime import datetime, timedelta
from flask_migrate import Migrate
import models
from models import User, Log, Help, Form, Student
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
    "https://jomc-news.vercel.app",
]

CORS(app, origins=ALLOWED_FRONTEND_ORIGINS, supports_credentials=True)
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
        return jsonify({'error': 'An error occurred. Please try again'}), 400

    try:
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Missing login credentials'}), 401

        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()

        if not user:
            return jsonify({'error': 'User not found'}), 401

        if not user.check_password(password):
            return jsonify({'error': 'Invalid password'}), 401

        return jsonify({'user': encode(user.to_dict()), 'expiry': datetime.utcnow() + timedelta(hours=171), 'token':generate_token(user.id)}), 200

    except Exception as e:
        log(f'[500] Error in /login route: {str(e)}', 'error')
        return jsonify({'error': 'Server error during login'}), 500

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

@app.route('/get_forms/<id>/<token>')
def forms(id, token):
    if id and token:
        user = User.query.filter_by(id=id).first()
        if user:
            if validate_token(token, user.id):
                forms = Form.query.filter_by(user_id=user.id).all()
                if forms:
                    return jsonify({'forms':[f.to_dict() for f in forms]}), 200
                return jsonify({'msg':'No forms found. Please add some'})
            return jsonify({'error':'Unauthorized'}), 401
        return jsonify({'error':'Failed to load account. Please reload the page or login again'}), 404
    return jsonify({'error':'Misssing data in request. Please, try again'}), 404

@app.route('/form/<id>')
def get_form(id):
    if id:
        form = Form.query.filter_by(id=id).first()
        if form:
            return jsonify({'form':form.to_dict()}), 200
        return jsonify({'error':'Page not found'}), 404
    return jsonify({'error':'Incomplete request'}), 400
    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=6500, host="0.0.0.0")

