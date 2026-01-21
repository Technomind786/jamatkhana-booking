from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = "jamatkhana_booking_secret_key"

# ---------- DATABASE CONNECTION ----------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Ammar.r007",
        database="wedding_booking"
    )

# ---------- HOME / HALL LIST ----------
@app.route("/")
def home():
    selected_date = request.args.get("date")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT hall_id, hall_name, location, description, capacity
        FROM wedding_halls
    """)
    halls_data = cursor.fetchall()

    halls = []
    for hall in halls_data:
        booked = False
        if selected_date:
            cursor.execute("""
                SELECT 1 FROM hall_bookings
                WHERE hall_id=%s AND event_date=%s
            """, (hall["hall_id"], selected_date))
            if cursor.fetchone():
                booked = True

        halls.append({
            "id": hall["hall_id"],
            "name": hall["hall_name"],
            "location": hall["location"],
            "description": hall["description"],
            "capacity": hall["capacity"],
            "booked": booked
        })

    conn.close()
    return render_template("halls.html", halls=halls, selected_date=selected_date)

# ---------- HALL DETAILS PAGE ----------
@app.route("/hall/<int:hall_id>")
def hall_details(hall_id):
    selected_date = request.args.get("date")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT hall_id, hall_name, location, description, capacity
        FROM wedding_halls
        WHERE hall_id=%s
    """, (hall_id,))
    hall = cursor.fetchone()

    booked = False
    if selected_date:
        cursor.execute("""
            SELECT 1 FROM hall_bookings
            WHERE hall_id=%s AND event_date=%s
        """, (hall_id, selected_date))
        if cursor.fetchone():
            booked = True

    conn.close()

    return render_template(
        "hall_details.html",
        hall=hall,
        booked=booked,
        selected_date=selected_date
    )

# ---------- RESERVE ----------
@app.route("/reserve", methods=["POST"])
def reserve():
    hall_id = request.form.get("hall_id")
    event_date = request.form.get("date")

    if not hall_id or not event_date:
        return "Date or hall missing."

    return redirect(url_for("payment", hall_id=hall_id, date=event_date))

# ---------- PAYMENT ----------
@app.route("/payment")
def payment():
    hall_id = request.args.get("hall_id")
    event_date = request.args.get("date")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT hall_name, location, capacity
        FROM wedding_halls
        WHERE hall_id=%s
    """, (hall_id,))
    hall = cursor.fetchone()

    conn.close()

    return render_template(
        "payment.html",
        hall=hall,
        hall_id=hall_id,
        date=event_date
    )

# ---------- CONFIRM PAYMENT ----------
@app.route("/confirm_payment", methods=["POST"])
def confirm_payment():
    hall_id = request.form.get("hall_id")
    event_date = request.form.get("date")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO hall_bookings (hall_id, event_date, status, hold_time)
        VALUES (%s, %s, 'BOOKED', %s)
    """, (hall_id, event_date, datetime.now()))

    conn.commit()
    conn.close()

    return render_template("success.html")

# ---------- ADMIN LOGIN ----------
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("username") == "admin" and request.form.get("password") == "admin123":
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        return render_template("admin_login.html", error="Invalid credentials")

    return render_template("admin_login.html")

# ---------- ADMIN DASHBOARD ----------
@app.route("/admin_dashboard")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT wh.hall_name, hb.event_date, hb.status
        FROM hall_bookings hb
        JOIN wedding_halls wh ON hb.hall_id = wh.hall_id
        ORDER BY hb.event_date DESC
    """)
    bookings = cursor.fetchall()

    conn.close()
    return render_template("admin_dashboard.html", bookings=bookings)

# ---------- ADMIN LOGOUT ----------
@app.route("/admin_logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
