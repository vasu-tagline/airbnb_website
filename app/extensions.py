from flask_mail import Mail
from flask_socketio import SocketIO

mail = Mail()   # ✅ no app here

socketio = SocketIO(cors_allowed_origins="*")