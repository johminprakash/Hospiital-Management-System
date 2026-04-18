import sqlite3

connection=sqlite3.connect("database.db")
cursor=connection.cursor()

command1="""CREATE TABLE IF NOT EXISTS admin
(admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
password TEXT)
"""
cursor.execute(command1)

command2="""CREATE TABLE IF NOT EXISTS doctor
(doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
 username TEXT UNIQUE,
 password TEXT,
 name TEXT,
 department_id INTEGER,
 specialization TEXT,
 qualification TEXT,
 experience_years INTEGER,
 phone TEXT,
 basic_time_slot INTEGER,
 follow_up INTEGER,
 normal_consultancy INTEGER,
 procedure INTEGER,
 is_active INTEGER,
 FOREIGN KEY (department_id) REFERENCES department(department_id)) 
 """
cursor.execute(command2)

command3="""CREATE TABLE IF NOT EXISTS patient(
 patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
 username TEXT UNIQUE,
 password TEXT,
 name TEXT,
 age INTEGER,
 gender TEXT,
 phone TEXT,
 is_active INTEGER)
 """
cursor.execute(command3)

command4="""CREATE TABLE IF NOT EXISTS appointment(
 appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
 doctor_id INTEGER,
 patient_id INTEGER,
 date TEXT,
 start_time TEXT,
 end_time TEXT,
 status INTEGER ,
 availability_id INTEGER, 
 consultancy_type TEXT,
 FOREIGN KEY(availability_id) REFERENCES doctor_availability(availability_id),
 FOREIGN KEY(doctor_id) REFERENCES doctor(doctor_id),
 FOREIGN KEY(patient_id) REFERENCES patient(patient_id))
 """
cursor.execute(command4)

command5="""CREATE TABLE IF NOT EXISTS doctor_availability(
 availability_id INTEGER PRIMARY KEY AUTOINCREMENT,
 doctor_id INTEGER,
 day TEXT,
 start_time TEXT,
 end_time TEXT,
 FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id))
 """
cursor.execute(command5)

command6="""CREATE TABLE IF NOT  EXISTS treatment(
 prescription_id INTEGER PRIMARY KEY AUTOINCREMENT,
 doctor_id INTEGER,
 patient_id INTEGER,
 appointment_id INTEGER,
 medicine TEXT,
 notes TEXT,
 FOREIGN KEY(doctor_id) REFERENCES doctor(doctor_id),
 FOREIGN KEY(patient_id) REFERENCES patient(patient_id),
 FOREIGN KEY (appointment_id) REFERENCES appointment(appointment_id))
 """
cursor.execute(command6)

command7="""CREATE TABLE IF NOT EXISTS department(
 department_id INTEGER PRIMARY KEY AUTOINCREMENT,
 department_name TEXT UNIQUE,
 description TEXT,
 doctors_registered INTEGER)
 """
cursor.execute(command7)

user="admin_bestmed"
password = "adbmmed8091"
command8="""INSERT INTO admin (username, password)
    VALUES (?, ?)
"""
cursor.execute(command8,(user,password))

departments = [
    ("Cardiology", "Heart-related treatments and surgeries", 0),
    ("Neurology", "Brain and nervous system disorders", 0),
    ("Orthopedics", "Bones, joints, and muscles", 0),
    ("Pediatrics", "Medical care for children", 0)
]

cursor.executemany("INSERT INTO department (department_name, description, doctors_registered) VALUES (?, ?, ?)",departments)
connection.commit()

connection.close()




