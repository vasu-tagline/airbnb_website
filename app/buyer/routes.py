from flask import Blueprint,render_template,request,flash,redirect,url_for,session
import os

from app.db import get_db
buyer_bp = Blueprint('buyer',__name__)




@buyer_bp.route("/buyer/dashboard")
def buyer_dashboard():
    if "user" not in session or session.get("role") != "buyer":
        return redirect(url_for("auth.login"))

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


@buyer_bp.route("/buyer/properties")
def buyer_properties():
    if "user" not in session or session.get("role") != "buyer":
        return redirect(url_for("auth.login"))

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
    
    

@buyer_bp.route("/property/<int:property_id>")
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


@buyer_bp.route("/payment/<int:property_id>")
def payment(property_id):

    # 🔐 Auth check
    if "user" not in session or session.get("role") != "buyer":
        return redirect(url_for("auth.login"))

    # username = session["user"]   # 👈 this EXISTS

    # conn = get_db()
    # cursor = conn.cursor()

    # # 0️⃣ Get buyer_id from username
    # cursor.execute(
    #     "SELECT id FROM users WHERE username = ?",
    #     (username,)
    # )
    # buyer = cursor.fetchone()
    
    buyer_id = session["user"][0]

    conn = get_db()
    cursor = conn.cursor()
    

    # 1️⃣ Get property details
    cursor.execute("""
        SELECT id, owner_id, price, deal_type, status
        FROM properties
        WHERE id = ?
    """, (property_id,))
    prop = cursor.fetchone()

    if not prop:
        conn.close()
        return "Property not found"

    if prop[4] != "available":
        conn.close()
        return "This property is no longer available"

    owner_id = prop[1]
    amount = prop[2]
    deal_type = prop[3]

    # 2️⃣ Save transaction
    cursor.execute("""
        INSERT INTO transactions
        (property_id, buyer_id, owner_id, deal_type, amount, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (property_id, buyer_id, owner_id, deal_type, amount, "completed"))

    # 3️⃣ Update property status
    new_status = "sold" if deal_type == "sale" else "rented"
    cursor.execute("""
        UPDATE properties
        SET status = ?
        WHERE id = ?
    """, (new_status, property_id))

    conn.commit()
    conn.close()

    return render_template("success.html")



@buyer_bp.route("/my-bookings")
def my_bookings():
    if "user" not in session or session.get("role") != "buyer":
        return redirect(url_for("auth.login"))


    conn = get_db()
    cursor = conn.cursor()
    
    username = session["user"]

    cursor.execute(
        "SELECT id FROM users WHERE username = ?",
        (username,)
    )
    buyer_id = cursor.fetchone()[0]

    cursor.execute("""
        SELECT 
            t.id,
            p.title,
            p.city,
            p.area,
            t.deal_type,
            t.amount,
            p.status,
            t.created_at,
            p.owner_id,
            p.contact_number,
            t.property_id,
            t.buyer_id,
            t.status
        FROM transactions t
        JOIN properties p ON t.property_id = p.id
        WHERE t.buyer_id = ?
        ORDER BY t.created_at DESC
    """, (buyer_id,))

    bookings = cursor.fetchall()
    conn.close()

    return render_template("my_bookings.html", bookings=bookings)



