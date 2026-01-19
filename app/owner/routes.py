from flask import Blueprint,render_template,request,flash,redirect,url_for,session,current_app
from werkzeug.utils import secure_filename
import os
from app.db import get_db

owner_bp = Blueprint('owner',__name__)

@owner_bp.route("/owner/dashboard")  
def owner_dashboard():
    return render_template("owner_dashboard.html")




@owner_bp.route("/add-property", methods=["GET", "POST"])
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
        image.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
        
        
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

        return redirect(url_for("owner.owner_dashboard"))

    return render_template("add_property.html")



@owner_bp.route("/my-properties")
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


@owner_bp.route("/edit_property/<int:property_id>", methods=["GET", "POST"])
def edit_property(property_id):
    if "user" not in session or session.get("role") != "owner":
        return redirect(url_for("auth.login"))

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

            return redirect(url_for("owner.my_properties"))

    return render_template("edit_property.html", property=property)




#delete
@owner_bp.route("/delete-property/<int:property_id>")
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

    return redirect(url_for("owner.my_properties"))
