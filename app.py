
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import oracledb
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "smartcare-local-demo-key")

# Oracle Database Free connection settings
DB_USER = os.getenv("ORACLE_USER", "APPOINTMENT_APP")
DB_PASSWORD = os.getenv("ORACLE_PASSWORD", "ChooseYourOwnStrongPassword123")
DB_HOST = os.getenv("ORACLE_HOST", "localhost")
DB_PORT = int(os.getenv("ORACLE_PORT", "1521"))
DB_SERVICE = os.getenv("ORACLE_SERVICE", "FREEPDB1")


def get_connection():
    """Connect Flask to Oracle Database."""
    if not DB_PASSWORD or DB_PASSWORD == "aarugarg":
        raise RuntimeError(
            "Set your Oracle password in the ORACLE_PASSWORD environment variable."
        )

    dsn = f"{DB_HOST}:{DB_PORT}/{DB_SERVICE}"
    return oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=dsn
    )


def get_columns(cursor, table_name):
    """Return column names for a table in the connected user's schema."""
    cursor.execute("""
        SELECT column_name
        FROM user_tab_columns
        WHERE table_name = :table_name
    """, {"table_name": table_name.upper()})

    return {row[0].lower() for row in cursor.fetchall()}


def next_id(cursor, table_name, id_column):
    """Generate the next ID for a simple single-user college demo."""
    cursor.execute(
        f"SELECT NVL(MAX({id_column}), 0) + 1 FROM {table_name}"
    )
    return cursor.fetchone()[0]


def insert_row(cursor, table_name, values):
    """Insert only the supplied columns that exist in the table."""
    columns = get_columns(cursor, table_name)
    selected = [(key, value) for key, value in values.items()
                if key.lower() in columns]

    if not selected:
        raise RuntimeError(
            f"No matching columns found for table {table_name}."
        )

    column_sql = ", ".join(key.upper() for key, _ in selected)
    bind_sql = ", ".join(f":v{i}" for i in range(len(selected)))
    params = {f"v{i}": value for i, (_, value) in enumerate(selected)}

    cursor.execute(
        f"INSERT INTO {table_name} ({column_sql}) VALUES ({bind_sql})",
        params
    )


def load_dashboard(search_term="", status_filter="", doctor_filter="",
                   date_filter=""):
    """Load dashboard totals, doctors, and filtered appointments."""

    data = {
        "total_appointments": 0,
        "total_patients": 0,
        "total_doctors": 0,
        "waiting_patients": 0,
        "completed_appointments": 0,
        "appointments": [],
        "doctors": [],
        "search_term": search_term,
        "selected_status": status_filter,
        "selected_doctor": doctor_filter,
        "selected_date": date_filter,
        "db_error": None
    }

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Doctors shown in the dashboard and booking form
        doctor_columns = get_columns(cursor, "DOCTORS")

        if {"doctor_id", "doctor_name", "specialization"}.issubset(
            doctor_columns
        ):
            if "is_available" in doctor_columns:
                cursor.execute("""
                    SELECT doctor_id, doctor_name, specialization
                    FROM doctors
                    WHERE UPPER(TRIM(is_available)) = 'Y'
                    ORDER BY doctor_id
                """)
            else:
                cursor.execute("""
                    SELECT doctor_id, doctor_name, specialization
                    FROM doctors
                    ORDER BY doctor_id
                """)

            data["doctors"] = cursor.fetchall()
            data["total_doctors"] = len(data["doctors"])

        # Dashboard totals
        cursor.execute("SELECT COUNT(*) FROM appointments")
        data["total_appointments"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM patients")
        data["total_patients"] = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM appointments
            WHERE UPPER(TRIM(status)) = 'WAITING'
        """)
        data["waiting_patients"] = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM appointments
            WHERE UPPER(TRIM(status)) = 'COMPLETED'
        """)
        data["completed_appointments"] = cursor.fetchone()[0]

        # Appointment table with optional search and filters
        sql = """
            SELECT
                a.appointment_id,
                a.token_number,
                a.patient_name,
                d.doctor_name,
                a.appointment_date,
                a.appointment_time,
                a.reason,
                a.status
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE 1 = 1
        """
        params = {}

        if search_term:
            sql += """
                AND (
                    LOWER(a.patient_name) LIKE :search_term
                    OR LOWER(a.reason) LIKE :search_term
                    OR TO_CHAR(a.token_number) LIKE :search_token
                )
            """
            params["search_term"] = f"%{search_term.lower()}%"
            params["search_token"] = f"%{search_term}%"

        if status_filter:
            sql += " AND UPPER(TRIM(a.status)) = :status_filter"
            params["status_filter"] = status_filter.upper()

        if doctor_filter:
            sql += " AND a.doctor_id = :doctor_id"
            params["doctor_id"] = int(doctor_filter)

        if date_filter:
            sql += """
                AND TRUNC(a.appointment_date) =
                    TO_DATE(:date_filter, 'YYYY-MM-DD')
            """
            params["date_filter"] = date_filter

        sql += " ORDER BY a.appointment_id ASC"

        cursor.execute(sql, params)
        data["appointments"] = cursor.fetchall()

    except Exception as error:
        app.logger.exception("Dashboard database error")
        data["db_error"] = str(error)

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return data


@app.route("/")
def home():
    return render_template(
        "index.html",
        **load_dashboard(
            search_term=request.args.get("q", "").strip(),
            status_filter=request.args.get("status", "").strip(),
            doctor_filter=request.args.get("doctor_id", "").strip(),
            date_filter=request.args.get("appointment_date", "").strip()
        )
    )


@app.route("/book", methods=["POST"])
def book_appointment():
    connection = None
    cursor = None

    try:
        patient_name = request.form.get("patient_name", "").strip()
        phone = request.form.get("phone", "").strip()
        doctor_id = request.form.get("doctor_id", "").strip()
        appointment_date = request.form.get("appointment_date", "").strip()
        appointment_time = request.form.get("appointment_time", "").strip()
        reason = request.form.get("reason", "").strip()

        if not all([
            patient_name, doctor_id, appointment_date,
            appointment_time, reason
        ]):
            flash("Please fill in all required fields.", "error")
            return redirect(url_for("home"))

        if phone and not phone.isdigit():
            flash("Phone number should contain digits only.", "error")
            return redirect(url_for("home"))

        booking_date = datetime.strptime(
            appointment_date, "%Y-%m-%d"
        ).date()

        booking_time = datetime.strptime(
            appointment_time, "%H:%M"
        ).time()

        if booking_date < datetime.today().date():
            flash("Please choose today or a future date.", "error")
            return redirect(url_for("home"))

        connection = get_connection()
        cursor = connection.cursor()

        # Check that the selected doctor exists and is available
        doctor_columns = get_columns(cursor, "DOCTORS")

        doctor_sql = """
            SELECT doctor_id
            FROM doctors
            WHERE doctor_id = :doctor_id
        """

        if "is_available" in doctor_columns:
            doctor_sql += " AND UPPER(TRIM(is_available)) = 'Y'"

        cursor.execute(doctor_sql, {"doctor_id": int(doctor_id)})

        if not cursor.fetchone():
            flash("Selected doctor is not available.", "error")
            return redirect(url_for("home"))

        # Create patient record
        patient_id = next_id(cursor, "patients", "patient_id")

        insert_row(cursor, "patients", {
            "patient_id": patient_id,
            "patient_name": patient_name,
            "name": patient_name,
            "phone": phone,
            "mobile": phone,
            "contact_number": phone
        })

        # Generate the next token for this doctor on this date
        cursor.execute("""
            SELECT NVL(MAX(token_number), 0) + 1
            FROM appointments
            WHERE TRUNC(appointment_date) = :appointment_day
              AND doctor_id = :doctor_id
        """, {
            "appointment_day": booking_date,
            "doctor_id": int(doctor_id)
        })

        token_number = cursor.fetchone()[0]
        appointment_id = next_id(
            cursor, "appointments", "appointment_id"
        )

        # Save appointment
        insert_row(cursor, "appointments", {
            "appointment_id": appointment_id,
            "patient_id": patient_id,
            "patient_name": patient_name,
            "doctor_id": int(doctor_id),
            "appointment_date": booking_date,
            "appointment_time": booking_time.strftime("%H:%M"),
            "token_number": token_number,
            "status": "WAITING",
            "reason": reason
        })

        connection.commit()

        flash(
            f"Appointment booked successfully! Your token number is "
            f"{token_number}.",
            "success"
        )

    except Exception:
        if connection:
            connection.rollback()

        app.logger.exception("Appointment booking failed")
        flash(
            "Booking failed. Please check the Oracle tables and columns "
            "and review the VS Code terminal.",
            "error"
        )

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return redirect(url_for("home"))


@app.route("/update_status/<int:appointment_id>", methods=["POST"])
def update_status(appointment_id):
    allowed_statuses = {
        "WAITING", "IN PROGRESS", "COMPLETED", "CANCELLED"
    }

    new_status = request.form.get("status", "").strip().upper()

    if new_status not in allowed_statuses:
        flash("Invalid appointment status.", "error")
        return redirect(url_for("home"))

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE appointments
            SET status = :status
            WHERE appointment_id = :appointment_id
        """, {
            "status": new_status,
            "appointment_id": appointment_id
        })

        if cursor.rowcount == 0:
            flash("Appointment not found.", "error")
        else:
            connection.commit()
            flash("Appointment status updated successfully.", "success")

    except Exception:
        if connection:
            connection.rollback()

        app.logger.exception("Status update failed")
        flash("Unable to update appointment status.", "error")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return redirect(url_for("home"))


@app.route("/api/status-chart")
def status_chart_api():
    """Return appointment status counts for the Chart.js doughnut chart."""

    data = {
        "WAITING": 0,
        "IN PROGRESS": 0,
        "COMPLETED": 0,
        "CANCELLED": 0
    }

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT UPPER(TRIM(status)), COUNT(*)
            FROM appointments
            GROUP BY UPPER(TRIM(status))
        """)

        for status, total in cursor.fetchall():
            if status in data:
                data[status] = total

        return jsonify(data)

    except Exception:
        app.logger.exception("Unable to load appointment status chart")
        return jsonify({
            "error": "Unable to load appointment status data"
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


if __name__ == "__main__":
    app.run(debug=True)
