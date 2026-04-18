from flask import Blueprint, render_template, redirect, request, url_for, session
import sqlite3, os

admin_logic_bp = Blueprint("admin_logic", __name__)

@admin_logic_bp.route('/admin_login', methods=['POST', 'GET'])
def login_check():
    if request.method == "POST":
        un = request.form.get('username')
        pw = request.form.get('password')
        db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        checklogin = "SELECT * FROM admin WHERE username=? AND password=?"
        cursor.execute(checklogin, (un, pw))
        logintrue = cursor.fetchall()
        if un == "":
            return render_template('admin_login.html', error="Username Field Required")
        if pw == "":
            return render_template('admin_login.html', error="Password Field Required")
        if logintrue:
            session['admin_id'] = logintrue[0][0]
            return render_template('admin_dashboard.html')
        return render_template('admin_login.html', error="Invalid credentials")
    return render_template('admin_login.html')

@admin_logic_bp.route('/admin/all_doctors')
def all_doctors():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    command = "SELECT doctor_id, name, specialization, qualification, experience_years, phone, is_active FROM doctor"
    cursor.execute(command)
    doctors = cursor.fetchall()
    full_data = []
    for d in doctors:
        did = d[0]
        command_av = "SELECT day, start_time, end_time FROM doctor_availability WHERE doctor_id=?"
        cursor.execute(command_av, (did,))
        av = cursor.fetchall()
        full_data.append((d, av))
    connection.close()
    return render_template("admin_doctors.html", doc=full_data)

@admin_logic_bp.route('/admin/edit_doctor', methods=['POST', 'GET'])
def edit_doctor():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    if request.method == "POST":
        did = request.form.get("did")
        name = request.form.get("name")
        special = request.form.get("special")
        quali = request.form.get("quali")
        exp = request.form.get("exp")
        phone = request.form.get("phone")
        active = request.form.get("status")
        command = "UPDATE doctor SET name=?, specialization=?, qualification=?, experience_years=?, phone=?, is_active=? WHERE doctor_id=?"
        cursor.execute(command, (name, special, quali, exp, phone, active, did))
        connection.commit()
        connection.close()
        return redirect(url_for('admin_logic.all_doctors'))
    did = request.args.get('did')
    connection.close()
    return render_template("admin_edit_doctor.html", did=did)

@admin_logic_bp.route('/admin/remove_doctor')
def remove_doctor():
    did = request.args.get("did")
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM doctor WHERE doctor_id=?", (did,))
    connection.commit()
    connection.close()
    return redirect(url_for('admin_logic.all_doctors'))

@admin_logic_bp.route('/admin/add_doctor', methods=['POST','GET'])
def add_doctor():
    if request.method == "POST":
        name = request.form.get('name', '').strip()
        special = request.form.get('special', '').strip()
        quali = request.form.get('quali', '').strip()
        exp = request.form.get('exp', '0').strip()
        phone = request.form.get('phone', '').strip()
        status = request.form.get('status', '0')

        try:
            exp = int(exp)
        except:
            exp = 0

        db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        command_insert = """INSERT INTO doctor
                            (name, specialization, qualification, experience_years, phone, is_active)
                            VALUES (?, ?, ?, ?, ?, ?)"""
        cursor.execute(command_insert, (name, special, quali, exp, phone, status))
        connection.commit()
        connection.close()

        return redirect(url_for('admin_logic.all_doctors'))

    return render_template('admin_add_doctor.html')


@admin_logic_bp.route('/admin/all_patients')
def all_patients():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("SELECT name, gender, age, phone FROM patient")
    patients = cursor.fetchall()
    connection.close()
    return render_template("admin_patients.html", pat=patients)

@admin_logic_bp.route('/admin/all_appointments')
def all_appointments():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    command = "SELECT a.appointment_id, d.name, p.name, a.date, a.start_time, a.end_time, a.status FROM appointment a JOIN doctor d ON d.doctor_id=a.doctor_id JOIN patient p ON p.patient_id=a.patient_id ORDER BY substr(a.date,7,4)||'-'||substr(a.date,4,2)||'-'||substr(a.date,1,2), a.start_time"
    cursor.execute(command)
    app = cursor.fetchall()
    connection.close()
    return render_template("admin_all_appointments.html", app=app)

@admin_logic_bp.route('/admin/search_patient', methods=['POST', 'GET'])
def search_patient():
    res = []
    if request.method == "POST":
        name = request.form.get("name")
        if name:  # make sure name is not None
            db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()
            cursor.execute("SELECT name, gender, age, phone FROM patient WHERE name=?", (name,))
            res = cursor.fetchall()
            connection.close()
    return render_template("admin_search_patient.html", res=res)


@admin_logic_bp.route('/admin/search_doctor', methods=['POST', 'GET'])
def search_doctor():
    res = []
    if request.method == "POST":
        name = request.form.get("name")
        if name:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()
            cursor.execute("SELECT doctor_id, name, specialization FROM doctor WHERE name=?", (name,))
            res = cursor.fetchall()
            connection.close()
    return render_template("admin_search_doctor.html", res=res)