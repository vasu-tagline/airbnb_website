from flask import Flask , render_template ,request,redirect,url_for,session,flash
import sqlite3
import os
from werkzeug.utils import secure_filename




app = Flask(__name__)
app.secret_key = "my_super_secret_key"


UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.after_request
def add_global_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

    
    
# ----> DATABASE 
def get_db():
    return sqlite3.connect("users.db")


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



@app.route("/register" , methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        #username, pass lai lyo
        username = request.form['username']
        password = request.form['password']
        role = request.form['user_type']
        email = request.form['email']
        
        #data base ma nakhi devanu
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (role, username, password , email) VALUES (?, ?, ?, ?)",
            (role, username, password , email)
        )
        conn.commit()
        conn.close()    
        return redirect(url_for('login'))
        
    return render_template("register.html")



@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    role = session.get("role")

    if role == "owner":
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





@app.route("/owner/dashboard")  
def owner_dashboard():
    return render_template("owner_dashboard.html")



@app.route("/buyer/dashboard")
def buyer_dashboard():
    return render_template("buyer_dashboard.html")



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
    # 🔐 Only owner allowed
    if "user" not in session or session.get("role") != "owner":
        return redirect(url_for("login"))



    conn = get_db()
    cursor = conn.cursor()

    # 1️⃣ get owner id
    cursor.execute(
        "SELECT id FROM users WHERE username=?",
        (session["user"],)
    )
    owner_id = cursor.fetchone()[0]

    # 2️⃣ get owner's properties
    cursor.execute("""
        SELECT * FROM properties
        WHERE owner_id=?
    """, (owner_id,))

    properties = cursor.fetchall()
    conn.close()

    return render_template("my_properties.html", properties=properties)




@app.route("/buyer/properties")
def buyer_properties():
    # 🔐 Only buyer allowed
    if "user" not in session or session.get("role") != "buyer":
        return redirect(url_for("login"))
    
    #badhu ley database mathi...
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
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
    """)  
    # cursor.execute("""SELECT * FROM properties """)
  
    properties = cursor.fetchall()
    conn.close()

    return render_template("buyer_properties.html", properties=properties)


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










# EDIT
@app.route("/edit_property/<int:property_id>", methods=["GET", "POST"])
def edit_property(property_id):
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

    # get property (ONLY if it belongs to owner)
    cursor.execute("""
        SELECT * FROM properties
        WHERE id=? AND owner_id=?
    """, (property_id, owner_id))

    property = cursor.fetchone()

    if not property:
        conn.close()
        return "Unauthorized access", 403

    if request.method == "POST":
        title = request.form["title"]
        price = request.form["price"]
        address = request.form["address"]
        description = request.form["description"]

        cursor.execute("""
            UPDATE properties
            SET title=?, price=?, address=?, description=?
            WHERE id=?
        """, (title, price, address, description, property_id))

        conn.commit()
        conn.close()

        return redirect(url_for("my_properties"))

    conn.close()
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


