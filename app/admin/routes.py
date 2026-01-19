from flask import Blueprint,render_template,request,flash,redirect,url_for,session
from app.db import get_db,create_property_table
admin_bp = Blueprint('admin',__name__)



@admin_bp.route("/admin/dashboard")
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


@admin_bp.route("/admin/users")
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


@admin_bp.route("/admin/delete-user/<int:user_id>")
def delete_user(user_id):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()

    # 1️⃣ Delete all properties of this user
    cursor.execute(
        "DELETE FROM properties WHERE owner_id=?",
        (user_id,)
    )

    # 2️⃣ Delete the user
    cursor.execute(
        "DELETE FROM users WHERE id=?",
        (user_id,)
    )

    conn.commit()
    conn.close()

    flash("User and all their properties deleted successfully", "success")
    return redirect(url_for("admin.admin_users"))


@admin_bp.route("/admin/edit-user/<int:user_id>", methods=["GET", "POST"])
def admin_edit_user(user_id):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()

    # GET user
    cursor.execute(
        "SELECT id, username, role, email FROM users WHERE id=?",
        (user_id,)
    )
    user = cursor.fetchone()

    if not user:
        conn.close()
        return "User not found", 404

    if request.method == "POST":
        username = request.form["username"]
        role = request.form["role"]
        email = request.form["email"]

        cursor.execute("""
            UPDATE users
            SET username=?, role=?, email=?
            WHERE id=?
        """, (username, role, email, user_id))

        conn.commit()
        conn.close()

        flash("User updated successfully", "success")
        return redirect(url_for("admin.admin_users"))

    conn.close()
    return render_template("admin_edit_user.html", user=user)



@admin_bp.route("/admin/delete-property/<int:pid>")
def admin_delete_property(pid):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    conn = get_db()
    conn.execute("DELETE FROM properties WHERE id=?", (pid,))
    conn.commit()
    conn.close()

    return redirect(url_for("admin.admin_properties"))



@admin_bp.route("/admin/properties")
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



@admin_bp.route("/admin/edit-property/<int:property_id>", methods=["GET", "POST"])
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
        return redirect(url_for("admin.admin_properties"))

    # 🔹 GET request → show edit form
    conn.close()
    return render_template(
        "admin_edit_property.html",
        property=property
    )
