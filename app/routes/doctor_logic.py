from flask import Blueprint, render_template, redirect, request, url_for, session
import sqlite3,os
from datetime import date,timedelta,datetime

doctor_logic_bp=Blueprint("doctor_logic",__name__)


@doctor_logic_bp.route('/doctor_login',methods=['POST','GET'])
def login_check():
    if(request.method=="POST"):
        un=request.form.get('username')
        pw=request.form.get('password')
        db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
        connection= sqlite3.connect(db_path)
        cursor=connection.cursor()
        checklogin="SELECT * from doctor WHERE username=? AND password=?"
        cursor.execute(checklogin,(un,pw))
        logintrue=cursor.fetchall()
        if(un==""):
           return render_template('doctor_login.html',error="Username Field Required")

        if(pw==""):
           return render_template('doctor_login.html',error="Password Field Required")
        if (logintrue):
            session['doctor_id']=logintrue[0][0]
            connection.close()
            return redirect(url_for('doctor_logic.dashboard')) 

        else:
            connection.close()
            return render_template('doctor_login.html',error="Invalid credentials")
    return render_template('doctor_login.html')

@doctor_logic_bp.route('/doctor_dashboard')
def dashboard():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
    connection= sqlite3.connect(db_path)
    cursor=connection.cursor()

    command_appointments="""SELECT p.name,p.patient_id,p.age,p.gender,a.date,a.start_time,a.end_time,a.appointment_id
    FROM patient p JOIN appointment a ON a.patient_id=p.patient_id
    WHERE a.doctor_id=? AND a.status=?"""
    cursor.execute(command_appointments,(session.get('doctor_id'),1))
    appointments=cursor.fetchall()

    sorted_appointments=[]
    dates=[]
    for i in appointments:
        if ((i[4],i[5]) not in dates):
            dates.append((i[4],i[5]))
    
    dt_dates=[]
    for d,t in dates:
        dt_dates.append(datetime.strptime(f"{d} {t}","%d-%m-%Y %H:%M"))
    dt_dates.sort()
    
    sorted_dates=[]
    for i in dt_dates:
        sorted_dates.append(i.strftime("%d-%m-%Y %H:%M"))

    sorted_appointments=[]
    for i in sorted_dates:
        parts=i.split(" ")
        dat=parts[0]
        tim=parts[1]
        for j in appointments:
            if (dat==j[4] and tim==j[5]):
                sorted_appointments.append(j)
                break
    
    finished_appointments=[]
    upcoming_appointments=[]
    for i in sorted_appointments:
        if(datetime.strptime(i[4],"%d-%m-%Y").date()<datetime.today().date()):
            finished_appointments.append(i)
        elif(datetime.strptime(i[4],"%d-%m-%Y").date()==datetime.today().date()):
            finished_appointments.append(i)
            upcoming_appointments.append(i)
        else:
            upcoming_appointments.append(i)
            


    command_patient_getter="SELECT DISTINCT p.name,p.age,p.gender FROM patient p JOIN appointment a ON a.patient_id=p.patient_id WHERE a.doctor_id=?"
    cursor.execute(command_patient_getter,(session.get('doctor_id'),))
    patients=cursor.fetchall()
    connection.close()
    return render_template('doctor_dashboard.html',app=upcoming_appointments,patients=patients,finished_appointments=finished_appointments)




@doctor_logic_bp.route('/doctor/my_profile')
def my_profile():
    doctor_id = session.get('doctor_id')

    db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    command_my_profile="SELECT name, specialization, qualification, experience_years, phone,basic_time_slot,follow_up,normal_consultancy,procedure FROM doctor WHERE doctor_id=?"
    cursor.execute(command_my_profile,(session.get('doctor_id'),))
    details=cursor.fetchone()
    
    command_appointments="""SELECT p.name,p.patient_id,p.age,p.gender,a.date,a.start_time,a.end_time,t.medicine,t.notes,a.appointment_id,a.status
    FROM patient p JOIN appointment a ON a.patient_id=p.patient_id
    LEFT JOIN treatment t ON t.appointment_id=a.appointment_id
    WHERE a.doctor_id=?"""
    cursor.execute(command_appointments,(session.get('doctor_id'),))
    appointments=cursor.fetchall()

    sorted_appointments=[]
    dates=[]
    for i in appointments:
        if ((i[4],i[5]) not in dates):
            dates.append((i[4],i[5]))
    
    dt_dates=[]
    for d,t in dates:
        dt_dates.append(datetime.strptime(f"{d} {t}","%d-%m-%Y %H:%M"))
    dt_dates.sort()
    
    sorted_dates=[]
    for i in dt_dates:
        sorted_dates.append(i.strftime("%d-%m-%Y %H:%M"))

    sorted_appointments=[]
    for i in sorted_dates:
        parts=i.split(" ")
        dat=parts[0]
        tim=parts[1]
        for j in appointments:
            if (dat==j[4] and tim==j[5]):
                sorted_appointments.append(j)
    connection.close()
    return render_template("doctor_myprofile.html",details=details,app=sorted_appointments)




@doctor_logic_bp.route('/doctor/change_password',methods=['POST','GET'])
def change_password():
    if(request.method=="POST"):
        db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
        connection= sqlite3.connect(db_path)
        cursor=connection.cursor()

        opw=request.form.get('opw')
        npw=request.form.get('npw')
        cnpw=request.form.get('cnpw')
        
        command_check_opw="SELECT password from doctor WHERE doctor_id=?"
        cursor.execute(command_check_opw,(session.get('doctor_id'),))
        old_pw=cursor.fetchone()

        if(opw!=old_pw[0]):
             return render_template("doctor_change_password.html",error="Old Password Wrong")
        if (npw!=cnpw):
            return render_template("doctor_hange_password.html",error="Password and Confirm Password does not match")
        if(len(npw)<8):
            return render_template("doctor_change_password.html",error="Password should be atleast 8 characters")
      
        command_edit_pofile="""UPDATE doctor
        SET password=?
        WHERE doctor_id=?"""
        cursor.execute(command_edit_pofile,(npw,session.get('doctor_id'),))
        connection.commit()
        connection.close()
        return redirect(url_for('doctor_logic.my_profile'))
    
    
    return render_template('doctor_change_password.html')





@doctor_logic_bp.route('/doctor/edit_profile',methods=['POST','GET'])
def edit_profile():
    if(request.method=="POST"):
        db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
        connection= sqlite3.connect(db_path)
        cursor=connection.cursor()

        name=request.form.get('name')
        special=request.form.get('special')
        quali=request.form.get('quali')
        exp=int(request.form.get('exp'))
        phone=request.form.get('phone')
        bts=int(request.form.get('bts'))
        follow_up=int(request.form.get('follow_up'))
        normal=int(request.form.get('normal'))
        procedure=int(request.form.get('procedure'))

        command_all_phone="SELECT phone FROM doctor"
        cursor.execute(command_all_phone)
        phones=cursor.fetchall()

        if phone in phones:
            return render_template('doctor_edit_profile.html',error="Phone Number already registered")

        if(bts<0 or exp<0 or follow_up<0 or normal<0 or procedure<0):
            return render_template('doctor_edit_profile.html',error="Fields cannot be negative")


        command_edit_pofile="""UPDATE doctor
        SET name=?,specialization=?,qualification=?,experience_years=?,phone=?,basic_time_slot=?,follow_up=?,normal_consultancy=?,procedure=?
        WHERE doctor_id=?"""
        cursor.execute(command_edit_pofile,(name,special,quali,exp,phone,bts,follow_up,normal,procedure,session.get('doctor_id')))
        connection.commit()
        connection.close()
        return redirect(url_for('doctor_logic.my_profile'))
    
    
    return render_template('doctor_edit_profile.html')




@doctor_logic_bp.route('/doctor/patient_history')
def patient_history():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
    connection= sqlite3.connect(db_path)
    cursor=connection.cursor()

    pat_id=request.args.get('patient_id')

    command_details="SELECT name,age,gender,phone FROM patient WHERE patient_id=?"
    cursor.execute(command_details,(pat_id,))
    details=cursor.fetchone()

    command_appointments="""SELECT d.name,dept.department_name,a.date,t.medicine,t.notes
        FROM appointment a JOIN doctor d ON d.doctor_id=a.doctor_id
        LEFT JOIN treatment t ON t.appointment_id=a.appointment_id
        JOIN department dept ON d.department_id=dept.department_id
        WHERE a.patient_id=?"""
    cursor.execute(command_appointments,(pat_id,))
    app=cursor.fetchall()

    connection.close()
    return render_template('doctor_patient_history.html',details=details,app=app)




@doctor_logic_bp.route('/doctor/show_availability')
def show_availability():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
    connection= sqlite3.connect(db_path)
    cursor=connection.cursor()

    command_show_availability="SELECT availability_id,day,start_time,end_time FROM doctor_availability WHERE doctor_id=? GROUP BY day"
    cursor.execute(command_show_availability,(session.get('doctor_id'),))
    avai=cursor.fetchall()

    connection.close()
    return render_template('doctor_show_availability.html',avai=avai)




@doctor_logic_bp.route("/doctor/edit_availability",methods=["POST","GET"])
def edit_availability():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
    connection= sqlite3.connect(db_path)
    cursor=connection.cursor()

    avai_id=request.args.get('availability_id')
    if (request.method=="POST"):
        day=request.form.get('day')
        start_time=request.form.get('start_time')
        end_time=request.form.get('end_time')

        command_update_availability="""UPDATE doctor_availability
        SET day=?,start_time=?,end_time=?
        WHERE availability_id=?"""
        cursor.execute(command_update_availability,(day,start_time,end_time,avai_id))
        connection.commit()

        connection.close()
        return redirect(url_for("doctor_logic.show_availability"))

    connection.close()
    return render_template("doctor_edit_availability.html",avai_id=avai_id)




@doctor_logic_bp.route("/doctor/add_availability",methods=["POST","GET"])
def add_availability():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
    connection= sqlite3.connect(db_path)
    cursor=connection.cursor()

    if (request.method=="POST"):
        day=request.form.get('day')
        start_time=request.form.get('start_time')
        end_time=request.form.get('end_time')

        command_update_availability="""INSERT INTO doctor_availability(doctor_id,day,start_time,end_time)
        VALUES(?,?,?,?)"""
        cursor.execute(command_update_availability,(session.get('doctor_id'),day,start_time,end_time,))
        connection.commit()

        connection.close()
        return redirect(url_for("doctor_logic.show_availability"))

    connection.close()
    return render_template("doctor_add_availability.html")




@doctor_logic_bp.route("/doctor/remove_availability")
def remove_availability():
        db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
        connection= sqlite3.connect(db_path)
        cursor=connection.cursor()

        avai_id=request.args.get('availability_id')
        
        command_update_availability="""DELETE FROM doctor_availability
        WHERE availability_id=?"""
        cursor.execute(command_update_availability,(avai_id))
        connection.commit()

        connection.close()
        return redirect(url_for("doctor_logic.show_availability"))




@doctor_logic_bp.route("/doctor/status_update",methods=['POST'])
def status_update():
        if(request.method=="POST"):
            db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
            connection= sqlite3.connect(db_path)
            cursor=connection.cursor()

            app_id=request.form.get('app_id')
            status=request.form.get('status')
            
            command_update_availability="""UPDATE appointment SET status=? WhERE appointment_id=?"""
            cursor.execute(command_update_availability,(status,app_id))
            connection.commit()

            connection.close()
            return redirect(url_for("doctor_logic.dashboard"))
        



@doctor_logic_bp.route("/doctor/edit_appointment",methods=['POST','GET'])
def edit_appointment():
    if(request.method=="POST"):
        db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
        connection= sqlite3.connect(db_path)
        cursor=connection.cursor()

        status=request.form.get('status')
        medicine=request.form.get('medicine')
        notes=request.form.get('notes')
        app=request.form.get('appointment_id')

        command_treat="""SELECT t.prescription_id 
        FROM treatment t JOIN appointment a 
        ON a.appointment_id=t.appointment_id 
        WHERE a.appointment_id=?"""
        cursor.execute(command_treat,(app,))
        treatment=cursor.fetchone()

        if (treatment):
            treat=treatment[0]
            command_update_treatment="UPDATE treatment SET medicine=?,notes=? WHERE prescription_id=?"
            cursor.execute(command_update_treatment,(medicine,notes,treat))
            connection.commit()
        else:
            command_details="SELECT doctor_id,patient_id FROM appointment WHERE appointment_id=?"
            cursor.execute(command_details,(app,))
            details=cursor.fetchone()
            command_insert_treatmet="INSERT into treatment (doctor_id,patient_id,appointment_id,medicine,notes) VALUES(?,?,?,?,?)"
            cursor.execute(command_insert_treatmet,(details[0],details[1],app,medicine,notes))

        command_update_appointment="UPDATE appointment SET status=? WHERE appointment_id=?"
        cursor.execute(command_update_appointment,(status,app))
        connection.commit()

        connection.close()
        return redirect(url_for('doctor_logic.my_profile'))
    app=request.args.get('app')
    return render_template('doctor_edit_appointment.html',app=app)