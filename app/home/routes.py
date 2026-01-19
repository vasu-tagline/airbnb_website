from flask import Blueprint,render_template,url_for,redirect,session

home_bp = Blueprint('home',__name__)

@home_bp.route('/')
def home():
    return render_template('main.html')


@home_bp.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("auth.login"))

    role = session.get("role")

    if role == "admin":
        return redirect(url_for("admin.admin_dashboard"))
    elif role == "owner":
        return redirect(url_for("owner.owner_dashboard"))
    elif role == "buyer":
        return redirect(url_for("buyer.buyer_dashboard"))
    else:
        return redirect(url_for("auth.login"))
    