from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "jamatkhana_booking_secret_key"

# ---------- DB CONNECTION ----------
def get_db():
    return psycopg2.connect(os.environ["DATABASE_URL"])

# ---------- INIT DB ----------
def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS halls (
        id SERIAL PRIMARY KEY,
        name TEXT,
        location TEXT,
        description TEXT,
        capacity INT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id SERIAL PRIMARY KEY,
        hall_id INT,
        event_date DATE,
        created_at TIMESTAMP
    )
    """)

    cur.execute("SELECT COUNT(*) FROM halls")
    if cur.fetchone()[0] == 0:
        cur.execute("""
        INSERT INTO halls (name, location, description, capacity) VALUES
        ('Burhani Hall','Indore','Ideal for Nikah and Majlis',20),
        ('Tayyebi Hall','Indore','Medium hall for functions',60),
        ('Mohammadi Hall','Indore','Large hall for Jamaat events',100)
        """)

    conn.commit()
    cur.close()
    conn.close()

# ---------- HOME ----------
@app.route("/")
def home():
    init_db()
    selected_date = request.args.get("date")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM halls")
    halls = cur.fetchall()

    hall_list = []
    for h in halls:
        booked = False
        if selected_date:
            cur.execute(
                "SELECT 1 FROM bookings WHERE hall_id=%s AND event_date=%s",
                (h[0], selected_date)
            )
            if cur.fetchone():
                booked = True

        hall_list.append({
            "id": h[0],
            "name": h[1],
            "location": h[2],
            "description": h[3],
            "capacity": h[4],
            "booked": booked
        })

    cur.close()
    conn.close()

    return render_template("halls.html", halls=hall_list, selected_date=selected_date)

# ---------- HALL DETAILS ----------
@app.route("/hall/<int:hall_id>")
def hall_details(hall_id):
    selected_date = request.args.get("date")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM halls WHERE id=%s", (hall_id,))
    h = cur.fetchone()

    booked = False
    if selected_date:
        cur.execute(
            "SELECT 1 FROM bookings WHERE hall_id=%s AND event_date=%s",
            (hall_id, selected_date)
        )
        if cur.fetchone():
            booked = True

    cur.close()
    conn.close()

    hall = {
        "hall_id": h[0],
        "hall_name": h[1],
        "location": h[2],
        "description": h[3],
        "capacity": h[4]
    }

    return render_template("hall_details.html", hall=hall, booked=booked, selected_date=selected_date)

# ---------- RESERVE ----------
@app.route("/reserve", methods=["POST"])
def reserve():
    return redirect(url_for(
        "payment",
        hall_id=request.form["hall_id"],
        date=request.form["date"]
    ))

# ---------- PAYMENT ----------
@app.route("/payment")
def payment():
    hall_id = request.args["hall_id"]
    date = request.args["date"]

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM halls WHERE id=%s", (hall_id,))
    h = cur.fetchone()
    cur.close()
    conn.close()

    hall = {
        "hall_name": h[1],
        "location": h[2],
        "capacity": h[4]
    }

    return render_template("payment.html", hall=hall, hall_id=hall_id, date=date)

# ---------- CONFIRM ----------
@app.route("/confirm_payment", methods=["POST"])
def confirm_payment():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO bookings (hall_id, event_date, created_at) VALUES (%s,%s,%s)",
        (request.form["hall_id"], request.form["date"], datetime.now())
    )
    conn.commit()
    cur.close()
    conn.close()

    return render_template("success.html")

# ---------- ADMIN ----------
@app.route("/admin", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        if request.form["username"]=="admin" and request.form["password"]=="admin123":
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
    return render_template("admin_login.html")

@app.route("/admin_dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT h.name, b.event_date, b.created_at
        FROM bookings b
        JOIN halls h ON h.id=b.hall_id
        ORDER BY b.created_at DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    bookings = [
        {
            "hall_name": r[0],
            "event_date": r[1],
            "status": "BOOKED"
        }
        for r in rows
    ]

    return render_template("admin_dashboard.html", bookings=bookings)

@app.route("/admin_logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))

if __name__ == "__main__":
    app.run()
