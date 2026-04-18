from flask import Blueprint,render_template,redirect,request,url_for,session
from datetime import date,timedelta,datetime
import sqlite3,os,json

patient_logic_bp=Blueprint("patient_logic",__name__)




@patient_logic_bp.route('/patient_login',methods=['POST','GET'])
def login_check():
    if(request.method=="POST"):
        un=request.form.get('username')
        pw=request.form.get('password')
        
        db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
        connection= sqlite3.connect(db_path)
        cursor=connection.cursor()

        checklogin="SELECT patient_id from patient WHERE username=? AND password=?"
        cursor.execute(checklogin,(un,pw))
        logintrue=cursor.fetchall()

        if(un==""):
           return render_template('patient_login.html',error="Username Field Required")
        if(pw==""):
           return render_template('patient_login.html',error="Password Field Required")
        
        if (logintrue):
            session['patient_id']=logintrue[0][0]
            connection.close()
            return redirect(url_for('patient_logic.department_getter')) 

        else:
            connection.close()
            return render_template('patient_login.html',error="Invalid credentials")
    return render_template('patient_login.html')





@patient_logic_bp.route('/patient_register',methods=['POST','GET'])
def register_check():
    if(request.method=="POST"):
        n=request.form.get('name')
        a=request.form.get('age')
        g=request.form.get('gender')
        ph=request.form.get('phone')
        un=request.form.get('username')
        pw=request.form.get('password')
        cpw=request.form.get('confirm_password')

        db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
        connection= sqlite3.connect(db_path)
        cursor=connection.cursor()

        check="SELECT 1 FROM patient WHERE phone=?"
        cursor.execute(check,(ph,))
        phcheck=cursor.fetchone()

        if(phcheck != None):
            return render_template('patient_register.html',error="Phone Number already registered")
        
        check="SELECT 1 FROM patient WHERE username=?"
        cursor.execute(check,(un,))
        uncheck=cursor.fetchone()

        if(uncheck != None):
            return render_template('patient_register.html',error="Username already taken")
        if (pw!=cpw):
            return render_template('patient_register.html',error="Password and Confirm Password does not match")
        if(len(pw)<8):
            return render_template('patient_register.html',error="Password must be atleast 8 characters")
        if(len(ph)!=10):
            return render_template('patient_register.html',error="Invalid Phone Number")        
        if(un==""):
           return render_template('patient_register.html',error="Username Field Required")
        if(pw==""):
           return render_template('patient_register.html',error="Password Field Required")
        
        register="INSERT INTO patient(username,password,name,age,gender,phone,is_active) VALUES(?,?,?,?,?,?,?)"
        cursor.execute(register,(un,pw,n,a,g,ph,1))
        connection.commit()

        connection.close()
        return redirect(url_for('patient_logic.login_check'))
    return render_template('patient_register.html')





@patient_logic_bp.route("/patient_dashboard")
def department_getter():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
    connection= sqlite3.connect(db_path)
    cursor=connection.cursor()

    command_dept="SELECT department_name,department_id,doctors_registered FROM department"
    cursor.execute(command_dept)
    departments=cursor.fetchall()
    print("Departments:", departments)
    connection.close()
    return render_template("patient_dashboard.html",departments=departments)




@patient_logic_bp.route("/patient_dashboard/department",methods=["POST","GET"])
def department_doctors():
    
    if (request.method=="POST"):
        slot=request.form.get("slot")
        c_type=request.form.get("c_type")
        if (slot and c_type):
            return redirect(url_for('patient_logic.appointment_booking',avai_id=slot,c_type=c_type))
        
    dept_id=request.args.get('dept_id',type=int)
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
    connection= sqlite3.connect(db_path)
    cursor=connection.cursor()

    command_dept_name="SELECT department_name FROM department WHERE department_id=?"
    cursor.execute(command_dept_name,(dept_id,))
    dept_name_row=cursor.fetchone()
    dept_name=dept_name_row[0]

    command_doctors="""SELECT d.doctor_id,d.name,d.basic_time_slot,d.follow_up,d.normal_consultancy,d.procedure,a.day,a.start_time,a.end_time,a.availability_id
    FROM doctor d JOIN doctor_availability a ON d.doctor_id=a.doctor_id
    WHERE d.department_id=? AND d.is_active=?
    ORDER BY d.doctor_id"""
    cursor.execute(command_doctors,(dept_id,1))
    rows=cursor.fetchall()

    doctors = {}
    for doc_id, doc_name, bts, follow,normal,procedure,day, start, end,avai_id in rows:
        if doc_id not in doctors:
            doctors[doc_id] = {
                "name": doc_name,
                "availability": {},
                "duration":[follow*bts,normal*bts,procedure*bts]   
            }
        if day not in doctors[doc_id]["availability"]:
            doctors[doc_id]["availability"][day] = {}
        doctors[doc_id]["availability"][day][avai_id]=f"{start}-{end}"
    print("Dept ID:", dept_id)
    print("Doctors fetched:", rows)
    print("Doctors dict:", doctors)
    connection.close()
    return render_template("patient_dashboard_department.html",doctors=doctors,dept_name=dept_name)




@patient_logic_bp.route("/patient_dashboard/doctor_profile")
def doctor_profile():
    doc_id=request.args.get('doc_id',type=int)
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
    connection= sqlite3.connect(db_path)
    cursor=connection.cursor()

    command_doctor_profile="SELECT * FROM doctor WHERE doctor_id=?"
    cursor.execute(command_doctor_profile,(doc_id,))
    rows=cursor.fetchone()
    connection.close()
    return render_template("patient_dashboard_doctor_profile.html",details=rows)




@patient_logic_bp.route("/patient_dashboard/my_profile")
def my_profile():
    patient_id = session.get('patient_id')

    db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    command_my_profile="SELECT name,age,gender,phone FROM patient WHERE patient_id=?"
    cursor.execute(command_my_profile,(session.get('patient_id'),))
    details=cursor.fetchone()

    command_my_appointments="""SELECT d.name,dept.department_name,a.date,a.start_time,a.end_time,t.medicine,t.notes,a.appointment_id 
    FROM appointment a 
    JOIN doctor d ON a.doctor_id=d.doctor_id 
    JOIN department dept ON d.department_id=dept.department_id
    LEFT JOIN treatment t ON a.appointment_id=t.appointment_id
    WHERE a.patient_id=?"""
    cursor.execute(command_my_appointments,(session.get('patient_id'),))
    app=cursor.fetchall()

    print("Session patient_id:", session.get('patient_id'))
    cursor.execute("SELECT * FROM appointment")
    print("All appointments:", cursor.fetchall())
    connection.close()
    return render_template("patient_dashboard_myprofile.html",details=details,app=app)




@patient_logic_bp.route('/patient_dashboard/edit_profile',methods=['POST','GET'])
def edit_profile():
    if(request.method=="POST"):
        db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
        connection= sqlite3.connect(db_path)
        cursor=connection.cursor()

        name=request.form.get('name')
        age=request.form.get('age')
        gender=request.form.get('gender')
        phone=request.form.get('phone')

        command_edit_pofile="""UPDATE patient
        SET name=?,age=?,gender=?,phone=?
        WHERE patient_id=?"""
        cursor.execute(command_edit_pofile,(name,age,gender,phone,session.get('patient_id')))
        connection.commit()
        connection.close()
        return redirect(url_for('patient_logic.my_profile'))
    
    
    return render_template('patient_dashboard_edit_profile.html')




@patient_logic_bp.route('/patient_dashboard/change_password',methods=['POST','GET'])
def change_password():
    if(request.method=="POST"):
        db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
        connection= sqlite3.connect(db_path)
        cursor=connection.cursor()

        opw=request.form.get('opw')
        npw=request.form.get('npw')
        cnpw=request.form.get('cnpw')
        
        command_check_opw="SELECT password from patient WHERE patient_id=?"
        cursor.execute(command_check_opw,(session.get('patient_id'),))
        old_pw=cursor.fetchone()

        if(opw!=old_pw[0]):
             connection.close()
             return render_template("patient_dashboard_change_password.html",error="Old Password Wrong")
        if (npw!=cnpw):
            connection.close()
            return render_template("patient_dashboard_change_password.html",error="Password and Confirm Password does not match")
        if(len(npw)<8):
            connection.close()
            return render_template("patient_dashboard_change_password.html",error="Password should be atleast 8 characters")
      
        command_edit_pofile="""UPDATE patient
        SET password=?
        WHERE patient_id=?"""
        cursor.execute(command_edit_pofile,(npw,session.get('patient_id'),))
        connection.commit()
        connection.close()
        return redirect(url_for('patient_logic.my_profile'))
    
    
    return render_template('patient_dashboard_change_password.html')




@patient_logic_bp.route("/patient_dashboard/appointment_booking", methods=["POST",'GET'])
def appointment_booking():

    if (request.method=="POST"):
        dic=json.loads(request.form.get("free_slots"))
        time=dic['start_time']+" to "+dic["end_time"]

        start=datetime.strptime(dic['start_time'],"%H:%M")
        end=datetime.strptime(dic['end_time'],"%H:%M")
        diff=(end-start).total_seconds()/60
        if (diff==dic['duration']):
            return redirect(url_for("patient_logic.confirm_appointment_details",avai_id=dic['avai_id'],date=dic['date'],time=time,c_type=dic['c_type']))
        elif(diff>dic['duration']):
            min=dic['start_time']
            max=(end-timedelta(minutes=int(dic['duration'])))
            arr=[]
            time=datetime.strptime(min,"%H:%M")
            while(time<=max):
                t=time.strftime("%H:%M")
                arr.append(t)
                time=time+timedelta(minutes=dic['duration'])
            return render_template("patient_dashboard_appointment_final.html",min=min,max=max,avai_id=dic['avai_id'],date=dic['date'],c_type=dic['c_type'],duration=dic['duration'],arr=arr)


    avai_id=request.args.get('avai_id',type=int)
    c_type=request.args.get('c_type')
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
    connection= sqlite3.connect(db_path)
    cursor=connection.cursor()
    
    command_day="SELECT day FROM doctor_availability WHERE availability_id=?"
    cursor.execute(command_day,(avai_id,))
    day=cursor.fetchone()
    day=day[0].lower()

    day_code={"monday":0,
              "tuesday":1,
              "wednesday":2,
              "thursday":3,
              "friday":4,
              "saturday":5,
              "sunday":6}
    
    start=date.today()
    days_between=(day_code[day]-start.weekday())%7
    first=start+timedelta(days=days_between)
    four_days=[]
    for i in range(4):
        dat=first+timedelta(weeks=i)
        parts=str(dat).split("-")
        parts=parts[::-1]
        formatted_date="-".join(parts)
        four_days.append(formatted_date)

    command_docname="""SELECT d.name,d.doctor_id 
    FROM doctor d JOIN doctor_availability a 
    ON d.doctor_id=a.doctor_id
    WHERE a.availability_id=? """
    cursor.execute(command_docname,(avai_id,))
    docname=cursor.fetchone()
    
    command_dept="""SELECT dept.department_name
    FROM department dept JOIN doctor d JOIN doctor_availability a
    ON d.doctor_id=a.doctor_id AND dept.department_id=d.department_id
    WHERE a.availability_id=?"""
    cursor.execute(command_dept,(avai_id,))
    deptname=cursor.fetchone()

    command_time="SELECT basic_time_slot,follow_up,normal_consultancy,procedure FROM doctor where doctor_id=?"
    cursor.execute(command_time,(docname[1],))
    time=cursor.fetchone()

    command_slot="SELECT day,start_time,end_time FROM doctor_availability WHERE availability_id=?"
    cursor.execute(command_slot,(avai_id,))
    slot=cursor.fetchone()

    duration=time[0]*time[int(c_type)]

    command_available_time="""SELECT date,start_time,end_time
     FROM appointment WHERE availability_id=? and status!=0
     ORDER BY start_time"""
    cursor.execute(command_available_time,(avai_id,))
    avail_time=cursor.fetchall()
    print("hi:",avail_time,four_days)

    sorted=[]
    fmt="%H:%M"
    for i in four_days:
        start_time_sort=[]
        end_time_sort=[]
        for j in avail_time:
            if j[0]==i:
                start_time_sort.append(datetime.strptime(j[1],fmt))
                end_time_sort.append(datetime.strptime(j[2],fmt))
        sorted.append([i,start_time_sort,end_time_sort])

    slots1=[]
    slots2=[]
    slots3=[]
    slots4=[]
   
    start_time=datetime.strptime(slot[1],fmt)
    end_time=datetime.strptime(slot[2],fmt)

    for i in range(4):
        found_slots=[]
        ele=sorted[i]
        if (ele[1]):
            diff=(ele[1][0]-start_time).total_seconds()/60
            if(diff>=duration):
                found_slots.append([start_time.strftime("%H:%M"),ele[1][0].strftime("%H:%M")])
            for j in range(len(ele[2])-1):
                diff=(ele[1][j+1]-ele[2][j]).total_seconds()/60
                if(diff>=duration):
                    found_slots.append([ele[2][j].strftime("%H:%M"),ele[1][j+1].strftime("%H:%M")])
            diff=(end_time-ele[2][-1]).total_seconds()/60
            if(diff>=duration):found_slots.append([ele[2][-1].strftime("%H:%M"),end_time.strftime("%H:%M")])
            for j in found_slots:
                if i==0:
                    slots1.append(j)
                elif i==1:
                    slots2.append(j)
                elif i==2:
                    slots3.append(j)
                elif i==3:
                    slots4.append(j)
        else:
            if i==0:
                    slots1.append([start_time.strftime("%H:%M"),end_time.strftime("%H:%M")])
            elif i==1:
                    slots2.append([start_time.strftime("%H:%M"),end_time.strftime("%H:%M")])
            elif i==2:
                    slots3.append([start_time.strftime("%H:%M"),end_time.strftime("%H:%M")])
            elif i==3:
                    slots4.append([start_time.strftime("%H:%M"),end_time.strftime("%H:%M")])
        
    connection.close()
    return render_template('patient_dashboard_appointment_booking.html',time=time,avai_id=avai_id,date=four_days,doctor=docname,department=deptname,c_type=c_type,duration=duration,slot=slot,slots1=slots1,slots2=slots2,slots3=slots3,slots4=slots4)





@patient_logic_bp.route("/patient_dashboard/final_booking",methods=["POST"])
def appointment_final():
    if (request.method=="POST"):
        date=request.args.get('date')
        c_type=request.args.get('c_type')
        duration=request.args.get('duration')
        avai_id=request.args.get('avai_id')
        start=request.form.get('start_time')

        start_time=datetime.strptime(start,"%H:%M")
        end=(start_time+timedelta(minutes=int(duration))).strftime("%H:%M")
        time=start+" to "+end
        return redirect(url_for("patient_logic.confirm_appointment_details",avai_id=avai_id,date=date,time=time,c_type=c_type))
        




@patient_logic_bp.route("/patient_dashboard/confirm_appointment_details")
def confirm_appointment_details():
    avai_id=request.args.get('avai_id')
    date=request.args.get('date')
    time=request.args.get('time')
    c_type=request.args.get('c_type')

    if(c_type=="1"):
        consultation="Follow-up"
    elif(c_type=="2"):
        consultation="Normal Consultancy"
    elif(c_type=="3"):
        consultation="Procedure"

    db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
    connection= sqlite3.connect(db_path)
    cursor=connection.cursor()

    command_get_doctor="""SELECT d.doctor_id,d.name,dept.department_name
    FROM doctor d JOIN doctor_availability a ON a.doctor_id=d.doctor_id
    JOIN department dept  ON dept.department_id=d.department_id"""
    cursor.execute(command_get_doctor)
    doctor=cursor.fetchone()
    connection.close()
    return render_template("patient_dashboard_confirm_appointment_details.html",doctor=doctor,time=time,consult=consultation,date=date,avai_id=avai_id)




@patient_logic_bp.route("/patient_dashboard/appointment_confirmed",methods=['POST'])
def appointment_confirmed():
    if(request.method=="POST"):
        db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        doctor_id = request.form.get("doctor_id")
        date      = request.form.get("date")
        time      = request.form.get("time")
        avai_id   = request.form.get("avai_id")
        consult=request.form.get("consult")

        times=time.split(" to ")

        command_appointment_booked="""INSERT INTO appointment(doctor_id,patient_id,date,start_time,end_time,status,availability_id,consultancy_type) 
        VALUES(?,?,?,?,?,?,?,?) """
        cursor.execute(command_appointment_booked,(doctor_id,session.get('patient_id'),date,times[0],times[1],1,avai_id,consult))
        connection.commit()

        appointment_id = cursor.lastrowid
        connection.close()
        return render_template('patient_dashboard_appointment_details.html',appid=appointment_id)
    
@patient_logic_bp.route("/patient_dashboard/search_doc",methods=['POST'])
def search_doc_by_name():
        if (request.method=="POST"):
            db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()

            docname=request.form.get("doc_name")

            command_doctor_profile="SELECT * FROM doctor WHERE name=?"
            cursor.execute(command_doctor_profile,(docname,))
            rows=cursor.fetchall()
            connection.close()
            return render_template("patient_dashboard_search_doctor_profile.html",details=rows)
        

