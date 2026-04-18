import sqlite3

connection = sqlite3.connect("database.db")
cursor = connection.cursor()

# List of all tables you want to inspect
tables = [
    "admin",
    "doctor",
    "patient",
    "appointment",
    "doctor_availability",
    "treatment",
    "department"
]

for table in tables:
    print(f"\n--- {table.upper()} ---")
    cursor.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

connection.close()