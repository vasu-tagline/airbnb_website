import os

from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = "my_super_secret_key"
    USER = os.getenv('MAIL_ID')
    PASS = os.getenv('MAIL_PASSWORD')
    
    
    MAIL_SERVER= 'smtp.gmail.com'
    MAIL_USE_TLS = True
    MAIL_USERNAME = USER
    MAIL_PASSWORD= PASS
    MAIL_PORT= 587
    MAIL_DEFAULT_SENDER= USER

    UPLOAD_FOLDER = os.path.join("app" , "static", "uploads")
    
