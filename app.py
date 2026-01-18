from flask import Flask , render_template ,request,redirect,url_for,session,flash
import sqlite3
import os
from werkzeug.utils import secure_filename
from flask_mail import Mail,Message
import random



from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = "my_super_secret_key"


UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


USER = os.getenv('MAIL_ID')
PASS = os.getenv('MAIL_PASSWORD')


# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = USER
app.config['MAIL_PASSWORD'] = PASS
app.config['MAIL_PORT'] = 587
app.config['MAIL_DEFAULT_SENDER'] = USER


mail = Mail(app)

@app.after_request
def add_global_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

   
    
def get_db():
    conn = sqlite3.connect("users.db", timeout=10)
    conn.row_factory = sqlite3.Row
    return conn



def create_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT
        )
    """)
    conn.commit()
    conn.close()
    

create_table()
# create_property_table()
# create_migration_table()
# run_migrations()



@app.route("/")
def apps():
    return render_template("main.html")


@app.route("/login" ,methods = ['GET', 'POST'] )
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
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid Username or password")
        
    return render_template("login.html")



@app.route("/register", methods=['GET', 'POST'])
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
            return redirect(url_for('register'))

        # Insert new user
        cursor.execute(
            "INSERT INTO users (role, username, password, email) VALUES (?, ?, ?, ?)",
            (role, username, password, email)
        )

        conn.commit()
        conn.close()
        flash("Registration successful. Please login.")
        return redirect(url_for('login'))

    return render_template("register.html")




@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    role = session.get("role")

    if role == "admin":
        return redirect(url_for("admin_dashboard"))
    elif role == "owner":
        return redirect(url_for("owner_dashboard"))
    elif role == "buyer":
        return redirect(url_for("buyer_dashboard"))
    else:
        return redirect(url_for("login"))
    
    

def create_property_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER,
            title TEXT,
            type TEXT,
            price INTEGER,
            description TEXT,
            image TEXT,
            contact_number TEXT,
            status TEXT DEFAULT 'available',
            deal_type TEXT,
            state TEXT,
            city TEXT,
            area TEXT
        )
    """)
    conn.commit()
    conn.close()
create_property_table()


@app.route("/admin/dashboard")
def admin_dashboard():

    if session.get("role") != "admin":
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()

    # 🔢 Total users
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    # 🏠 Total properties
    cursor.execute("SELECT COUNT(*) FROM properties")
    total_properties = cursor.fetchone()[0]

    # ⏳ Pending properties
    cursor.execute("SELECT COUNT(*) FROM properties WHERE status='pending'")
    pending_properties = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_properties=total_properties,
        pending_properties=pending_properties
    )


@app.route("/admin/users")
def admin_users():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    conn = get_db()
    users = conn.execute("""
        SELECT id, username, role, email
        FROM users
        WHERE role != 'admin'
    """).fetchall()
    conn.close()

    return render_template("admin_users.html", users=users)



@app.route("/admin/delete-user/<int:user_id>")
def delete_user(user_id):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    conn = get_db()
    conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("admin_users"))

@app.route("/admin/properties")
def admin_properties():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    conn = get_db()
    props = conn.execute("""
        SELECT p.*, u.username
        FROM properties p
        LEFT JOIN users u ON p.owner_id = u.id
    """).fetchall()
    conn.close()

    return render_template("admin_properties.html", properties=props)


@app.route("/admin/delete-property/<int:pid>")
def admin_delete_property(pid):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    conn = get_db()
    conn.execute("DELETE FROM properties WHERE id=?", (pid,))
    conn.commit()
    conn.close()

    return redirect(url_for("admin_properties"))


@app.route("/admin/edit-property/<int:property_id>", methods=["GET", "POST"])
def admin_edit_property(property_id):

    # 🔐 Admin protection
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()

    # 🔹 Fetch property
    cursor.execute("SELECT * FROM properties WHERE id=?", (property_id,))
    property = cursor.fetchone()

    if not property:
        conn.close()
        return "Property not found", 404

    # 🔹 Handle update
    if request.method == "POST":
        title = request.form.get("title")
        price = request.form.get("price")
        description = request.form.get("description")
        deal_type = request.form.get("deal_type")
        state = request.form.get("state")
        city = request.form.get("city")
        area = request.form.get("area")
        status = request.form.get("status")

        # 🔸 Validation
        if not title or not price or not deal_type:
            flash("Required fields are missing", "danger")
            conn.close()
            return redirect(request.url)

        # 🔹 Update query
        cursor.execute("""
            UPDATE properties
            SET title=?,
                price=?,
                description=?,
                deal_type=?,
                state=?,
                city=?,
                area=?,
                status=?
            WHERE id=?
        """, (
            title,
            price,
            description,
            deal_type,
            state,
            city,
            area,
            status,
            property_id
        ))

        conn.commit()
        conn.close()

        flash("Property updated successfully", "success")
        return redirect(url_for("admin_properties"))

    # 🔹 GET request → show edit form
    conn.close()
    return render_template(
        "admin_edit_property.html",
        property=property
    )




@app.route("/owner/dashboard")  
def owner_dashboard():
    return render_template("owner_dashboard.html")


@app.route("/buyer/dashboard")
def buyer_dashboard():
    if "user" not in session or session.get("role") != "buyer":
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, role, username, password , email
        FROM users
        WHERE username = ?
    """, (session["user"],))

    buyer = cursor.fetchone()
    conn.close()

    return render_template("buyer_dashboard.html", buyer=buyer)




@app.route("/add-property", methods=["GET", "POST"])
def add_property():
    if "user" not in session or session.get("role") != "owner":
        return redirect(url_for("login"))
    if request.method == "POST":
        title = request.form["title"]
        type_ = request.form["type"]
        price = request.form["price"]
        # address = request.form["address"]
        description = request.form["description"]
        contact_number = request.form["mobile"]
        deal_type = request.form["deal_type"]
        state = request.form["state"]
        city = request.form["city"]
        area = request.form["area"]
        
        # IMAGE PART
        image = request.files["image"]
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        
        
        conn = get_db()
        cursor = conn.cursor()
         
        # get owner id
        cursor.execute(
            "SELECT id FROM users WHERE username=?",
            (session["user"],)
        )
        owner_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO properties
            (owner_id, title, type, price, description,contact_number,deal_type,state,city,area,image)
            VALUES (?, ?, ?, ?,?,?,?,?,?,?,?)
        """, (owner_id, title, type_, price, description,contact_number,deal_type,state,city,area,filename))

        conn.commit()
        conn.close()

        return redirect(url_for("owner_dashboard"))

    return render_template("add_property.html")



@app.route("/my-properties")
def my_properties():
    # Only owner allowed
    if "user" not in session or session.get("role") != "owner":
        return redirect(url_for("login"))



    conn = get_db()
    cursor = conn.cursor()

    # get owner id
    cursor.execute(
        "SELECT id FROM users WHERE username=?",
        (session["user"],)
    )
    owner_id = cursor.fetchone()[0]

    # get owner's properties
    cursor.execute("""
        SELECT * FROM properties
        WHERE owner_id=?
    """, (owner_id,))

    properties = cursor.fetchall()
    conn.close()

    return render_template("my_properties.html", properties=properties)


@app.route("/buyer/properties")
def buyer_properties():
    if "user" not in session or session.get("role") != "buyer":
        return redirect(url_for("login"))

    state = request.args.get("state")
    city = request.args.get("city")
    deal_type = request.args.get("deal_type")
    max_price = request.args.get("max_price")

    conn = get_db()
    cursor = conn.cursor()

    query = """
        SELECT 
            p.id,
            p.title,
            p.price,
            p.description,
            p.image,
            p.contact_number,
            p.status,
            u.username,
            p.owner_id,
            p.type,
            p.deal_type,
            p.state,
            p.city,
            p.area
        FROM properties p
        JOIN users u ON p.owner_id = u.id
        WHERE 1=1
    """

    params = []

    if state:
        query += " AND p.state = ?"
        params.append(state)

    if city:
        query += " AND p.city = ?"
        params.append(city)

    if deal_type:
        query += " AND p.deal_type = ?"
        params.append(deal_type)

    if max_price:
        query += " AND p.price <= ?"
        params.append(max_price)

    cursor.execute(query, params)
    properties = cursor.fetchall()
    conn.close()

    return render_template(
        "buyer_properties.html",
        properties=properties,
        state=state,
        city=city,
        deal_type=deal_type,
        max_price=max_price
    )


@app.route("/property/<int:property_id>")
def property_details(property_id):
    
    

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            p.id,
            p.title,
            p.price,
            p.description,
            p.image,
            p.contact_number,
            p.status,
            u.username,
            p.type,
            p.deal_type,
            p.state,
            p.city,
            p.area
        FROM properties p
        JOIN users u ON p.owner_id = u.id
        WHERE p.id = ?
    """, (property_id,))

    property = cursor.fetchone()
    conn.close()

    return render_template("property_details.html", property=property)


@app.route("/payment")
def payment():
    return render_template("success.html")

@app.route("/home")
def home():
    username = session.get("user")
    
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE  username=? ",
        (username,)
    )
    user = cursor.fetchone()
    conn.close()
    
    return render_template("home.html" , user= user)


@app.route('/forgotpassword', methods=['GET', 'POST'])
def forgotpassword():
    if request.method == 'POST':
        email = request.form.get('email')

        otp = random.randint(100000, 999999)

        body = f"Your OTP is {otp}"
        subject = "Forgot Password"

        msg = Message(
            subject=subject,
            sender=app.config['MAIL_USERNAME'],
            recipients=[email]
        )
        msg.body = body
        mail.send(msg)

        session['otp'] = otp
        session['email'] = email

        return redirect(url_for('otppage'))

    return render_template('forgotpassword.html')



@app.route('/otppage', methods=['GET', 'POST'])
def otppage():
    if request.method == 'POST':
        user_otp = request.form.get('otp')
        saved_otp = session.get('otp')

        if saved_otp and int(user_otp) == saved_otp:
            return redirect(url_for('changepassword'))
        else:
            return "Wrong OTP"

    return render_template('otppage.html')


@app.route('/changepassword', methods=['GET', 'POST'])
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

        return redirect(url_for('login'))

    return render_template('changepassword.html')



# EDIT
@app.route("/edit_property/<int:property_id>", methods=["GET", "POST"])
def edit_property(property_id):
    if "user" not in session or session.get("role") != "owner":
        return redirect(url_for("login"))

    with get_db() as conn:
        cursor = conn.cursor()

        # get owner id
        cursor.execute("SELECT id FROM users WHERE username=?", (session["user"],))
        owner_id = cursor.fetchone()[0]

        # get property
        cursor.execute("SELECT * FROM properties WHERE id=? AND owner_id=?", (property_id, owner_id))
        property = cursor.fetchone()

        if not property:
            return "Unauthorized access", 403

        if request.method == "POST":
            title = request.form["title"]
            price = request.form["price"]
            contact_number = request.form["contact_number"]
            description = request.form["description"]

            cursor.execute("""
                UPDATE properties
                SET title=?, price=?, contact_number=?, description=?
                WHERE id=?
            """, (title, price, contact_number, description, property_id))
            conn.commit()

            return redirect(url_for("my_properties"))

    return render_template("edit_property.html", property=property)




#delete
@app.route("/delete-property/<int:property_id>")
def delete_property(property_id):
    if "user" not in session or session.get("role") != "owner":
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()

    # get owner id
    cursor.execute(
        "SELECT id FROM users WHERE username=?",
        (session["user"],)
    )
    owner_id = cursor.fetchone()[0]

    # delete only if owned by user
    cursor.execute("""
        DELETE FROM properties
        WHERE id=? AND owner_id=?
    """, (property_id, owner_id))

    conn.commit()
    conn.close()

    return redirect(url_for("my_properties"))



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(debug=True)




