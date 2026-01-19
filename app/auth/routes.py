from flask import Blueprint,render_template,request,flash,redirect,url_for,session
from app.db import get_db
import random
from flask_mail import Message
from app.extensions import mail

auth_bp = Blueprint('auth',__name__)




@auth_bp.route("/login" ,methods = ['GET', 'POST'] )
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        
        
        #check kare che ; valid che ke ny e 
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE  username=? AND password=?",
            (username,password)
        )
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session["user"] = user[2]      # username
            session["role"] = user[1]      # role
            return redirect(url_for("home.dashboard"))
        else:
            flash("Invalid Username or password")
        
    return render_template("login.html")



@auth_bp.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['user_type']
        email = request.form['email']

        conn = get_db()
        cursor = conn.cursor()

        # Check if username or email already exists
        cursor.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (username, email)
        )
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Username or Email already exists. Please choose another.")
            conn.close()
            return redirect(url_for('auth.register'))

        # Insert new user
        cursor.execute(
            "INSERT INTO users (role, username, password, email) VALUES (?, ?, ?, ?)",
            (role, username, password, email)
        )

        conn.commit()
        conn.close()
        flash("Registration successful. Please login.")
        return redirect(url_for('auth.login'))

    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))



@auth_bp.route('/forgotpassword', methods=['GET', 'POST'])
def forgotpassword():
    if request.method == 'POST':
        email = request.form.get('email')

        otp = random.randint(100000, 999999)

        msg = Message(
            subject="Forgot Password",
            recipients=[email],
            body=f"Your OTP is {otp}"
        )

        mail.send(msg)

        session['otp'] = otp
        session['email'] = email

        return redirect(url_for('auth.otppage'))

    return render_template('forgotpassword.html')




@auth_bp.route('/otppage', methods=['GET', 'POST'])
def otppage():
    if request.method == 'POST':
        user_otp = request.form.get('otp')
        saved_otp = session.get('otp')

        if saved_otp and int(user_otp) == saved_otp:
            return redirect(url_for('auth.changepassword'))
        else:
            return "Wrong OTP"

    return render_template('otppage.html')


@auth_bp.route('/changepassword', methods=['GET', 'POST'])
def changepassword():
    if request.method == 'POST':
        password = request.form.get('password')
        email = session.get('email')

        if not email:
            return "Session expired. Try again."

        # Connect to DB
        conn = get_db()
        cursor = conn.cursor()

        # Update password for the user with this email
        cursor.execute("UPDATE users SET password = ? WHERE email = ?", (password, email))
        conn.commit()
        conn.close()

        # Clear session
        session.pop('otp', None)
        session.pop('email', None)

        return redirect(url_for('auth.login'))

    return render_template('changepassword.html')
