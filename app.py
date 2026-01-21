from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "jamatkhana_booking_secret_key"

# --------------------------------------------------
# HOME PAGE (NO DATABASE – SAFE FOR RENDER)
# --------------------------------------------------
@app.route("/")
def home():
    selected_date = request.args.get("date")

    halls = [
        {
            "id": 1,
            "name": "Burhani Hall",
            "location": "Indore",
            "description": "Ideal for Nikah, Majlis and community gatherings.",
            "capacity": 20,
            "booked": False
        },
        {
            "id": 2,
            "name": "Tayyebi Hall",
            "location": "Indore",
            "description": "Medium sized hall suitable for most functions.",
            "capacity": 60,
            "booked": False
        },
        {
            "id": 3,
            "name": "Mohammadi Hall",
            "location": "Indore",
            "description": "Large hall for major Jamaat events.",
            "capacity": 100,
            "booked": False
        }
    ]

    return render_template("halls.html", halls=halls, selected_date=selected_date)

# --------------------------------------------------
# HALL DETAILS PAGE
# --------------------------------------------------
@app.route("/hall/<int:hall_id>")
def hall_details(hall_id):
    selected_date = request.args.get("date")

    hall_map = {
        1: {
            "hall_id": 1,
            "hall_name": "Burhani Hall",
            "location": "Indore",
            "description": "Ideal for Nikah, Majlis and community gatherings.",
            "capacity": 20
        },
        2: {
            "hall_id": 2,
            "hall_name": "Tayyebi Hall",
            "location": "Indore",
            "description": "Medium sized hall suitable for most functions.",
            "capacity": 60
        },
        3: {
            "hall_id": 3,
            "hall_name": "Mohammadi Hall",
            "location": "Indore",
            "description": "Large hall for major Jamaat events.",
            "capacity": 100
        }
    }

    hall = hall_map.get(hall_id)

    return render_template(
        "hall_details.html",
        hall=hall,
        booked=False,
        selected_date=selected_date
    )

# --------------------------------------------------
# RESERVE → PAYMENT
# --------------------------------------------------
@app.route("/reserve", methods=["POST"])
def reserve():
    hall_id = request.form.get("hall_id")
    date = request.form.get("date")
    return redirect(url_for("payment", hall_id=hall_id, date=date))

@app.route("/payment")
def payment():
    hall_id = request.args.get("hall_id")
    date = request.args.get("date")

    hall_map = {
        "1": {"hall_name": "Burhani Hall", "location": "Indore", "capacity": 20},
        "2": {"hall_name": "Tayyebi Hall", "location": "Indore", "capacity": 60},
        "3": {"hall_name": "Mohammadi Hall", "location": "Indore", "capacity": 100},
    }

    hall = hall_map.get(hall_id)

    return render_template(
        "payment.html",
        hall=hall,
        hall_id=hall_id,
        date=date
    )

# --------------------------------------------------
# CONFIRM PAYMENT (NO DB)
# --------------------------------------------------
@app.route("/confirm_payment", methods=["POST"])
def confirm_payment():
    return render_template("success.html")

# --------------------------------------------------
# ADMIN LOGIN
# --------------------------------------------------
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("username") == "admin" and request.form.get("password") == "admin123":
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        return render_template("admin_login.html", error="Invalid credentials")

    return render_template("admin_login.html")

# --------------------------------------------------
# ADMIN DASHBOARD (STATIC DATA FOR DEMO)
# --------------------------------------------------
@app.route("/admin_dashboard")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    bookings = [
        {"hall_name": "Burhani Hall", "event_date": "2026-02-01", "status": "BOOKED"},
        {"hall_name": "Tayyebi Hall", "event_date": "2026-02-05", "status": "BOOKED"},
    ]

    return render_template("admin_dashboard.html", bookings=bookings)

# --------------------------------------------------
# ADMIN LOGOUT
# --------------------------------------------------
@app.route("/admin_logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))

# --------------------------------------------------
# RUN
# --------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
