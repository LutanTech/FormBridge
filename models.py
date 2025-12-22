from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from utils import generate_random_id, generate_otp , generate_account_id
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

def get_offset_time_string():
    return (datetime.utcnow() + timedelta(hours=3)).isoformat()

class User(db.Model):
    id = db.Column(db.String(10), primary_key=True, default=generate_account_id)
    username = db.Column(db.String(255), unique=True)
    email = db.Column(db.String(255), unique=True)
    phone = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(512), nullable=False)
    joined = db.Column(db.String(), default=get_offset_time_string)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    level = db.Column(db.String(10), default='1')
    devices = db.Column(db.Integer, default=2)
    otp = db.Column(db.String(5))
    is_deleted = db.Column(db.Boolean, default=False)
    two_fa = db.Column(db.Boolean, default=False)
    twofa_secret = db.Column(db.String(32), nullable=True)
    blocked = db.Column(db.Text)
    reported = db.Column(db.Text)
    reportedActions = db.Column(db.Text)
    
    
    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    
    def to_dict(self):
        return {
            'id':self.id,
            'username': self.username,
            'email':self.email,
            'phone':self.phone,
            'joined':self.joined,
            'is_active':self.is_active,
            'is_verified':self.is_verified,
            'level':self.level,
            'devices':self.devices,
            'two_fa':True if self.twofa_secret else False,
            'blocked': json.loads(self.blocked) if self.blocked else [],
            'reported': json.loads(self.reported) if self.reported else []
        }    
    

class Log(db.Model):
   id = db.Column(db.String(6), primary_key=True)
   type = db.Column(db.String(20))
   content = db.Column(db.Text)
   requestor = db.Column(db.Text)
   at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=0))
   
   
   def to_dict(self):
       s = self
       return{
           'id':s.id,
           'type':s.type,
           'content': s.content,
           'info' : s.requestor,
           'at': s.at
           
       }
       

class Help(db.Model):
    id = db.Column(db.String(6), primary_key=True, default=lambda: generate_random_id(6))
    email = db.Column(db.String(255), nullable=False, unique=True)
    image = db.Column(db.Text(), nullable=True)
    text= db.Column(db.Text(), nullable=True)
    at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=3))

class Form(db.Model):
    id = db.Column(db.String(6), primary_key=True, default=lambda: generate_random_id(6))
    user_id = db.Column(db.String(10), nullable=False)
    added = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=3))
    opened = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=3))
    deadline = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=27))
    name_str = db.Column(db.String(255))  
    desc = db.Column(db.String(512))
    instructions = db.Column(db.String(512))
    is_open = db.Column(db.Boolean, default=True)
    inputs = db.Column(db.Text)
    selects = db.Column(db.Text, nullable=True)
    name = db.Column(db.Boolean, default=False)
    age = db.Column(db.Boolean, default=False)
    phone = db.Column(db.Boolean, default=False)
    adm = db.Column(db.Boolean, default=False)
    email = db.Column(db.Boolean, default=False)
    topic = db.Column(db.Boolean, default=False)
    assignment = db.Column(db.Boolean, default=False)
    units = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'added': self.added.isoformat() if self.added else None,
            'opened': self.opened.isoformat() if self.opened else None,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'name_str': self.name_str,
            'desc': self.desc,
            'instructions': self.instructions,
            'is_open': self.is_open,
            'inputs': self.inputs,
            'selects': self.selects,
            'name': self.name,
            'age': self.age,
            'phone': self.phone,
            'adm': self.adm,
            'email': self.email,
            'topic': self.topic,
            'assignment': self.assignment,
            'units': self.units,
        }
    def to_v_dict(self):
        return {
            'id': self.id,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'name_str': self.name_str,
            'instructions': self.instructions,
            'is_open': self.is_open,
            'inputs': self.inputs,
            'selects': self.selects,
        }
        

    
class Submission(db.Model):
    id = db.Column(db.String(10), primary_key=True, default=lambda: generate_random_id(10))
    form_id = db.Column(db.String(10), nullable=False)
    instructor = db.Column(db.String(10),nullable=False)
    name = db.Column(db.String(255), nullable=True)
    age = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(255), nullable=True)
    adm = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    topic = db.Column(db.String(255), nullable=True)
    assignment = db.Column(db.String(255), nullable=True)
    selects = db.Column(db.Text, nullable=True)
    units = db.Column(db.String(255), nullable=True)
    at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=3))
    
    def to_dict(self):
        return {
            "id": self.id,
            "form_id": self.form_id,
            "instructor": self.instructor,
            "name": self.name,
            "age": self.age,
            "phone": self.phone,
            "adm": self.adm,
            "email": self.email,
            "topic": self.topic,
            "assignment": self.assignment,
            "units": self.units,
            "selects": self.selects,
            "at": self.at.isoformat() if self.at else None
    }

    
class Device(db.Model):
    id = db.Column(db.String(10), primary_key=True, default=lambda: generate_random_id(10))
    user_id = db.Column(db.String(10), nullable=False)
    first_login = db.Column(db.DateTime,default=lambda: datetime.utcnow() + timedelta(hours=3))
    last_login = db.Column(db.DateTime,default=lambda: datetime.utcnow() + timedelta(hours=3))
    ua = db.Column(db.String(1024), nullable=True)
    ip = db.Column(db.String(45), nullable=False)  

    def to_dict(self):
        return {
            'id': self.id,
            'ua': self.ua,
            'ip': self.ip,
            'l': self.last_login.isoformat()
        }

    