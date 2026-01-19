from flask import Blueprint,render_template,request,flash,redirect,url_for,session
import os

from app.db import get_db
buyer_bp = Blueprint('buyer',__name__)




@buyer_bp.route("/buyer/dashboard")
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


@buyer_bp.route("/buyer/properties")
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


@buyer_bp.route("/payment")
def payment():
    return render_template("success.html")    