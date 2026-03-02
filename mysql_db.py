import json
import mysql.connector
from datetime import datetime

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "face_recognition"
}

# ---------- CONNECTION ----------
def get_db():
    return mysql.connector.connect(
        **DB_CONFIG,
        autocommit=False,
        buffered=True,
        use_pure=True,   # IMPORTANT: avoids C-extension crash
    )

# ---------- INSERT EMPLOYEE ----------
def insert_employee(name, embedding):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO employees (name, embedding) VALUES (%s, %s)",
        (name, json.dumps(embedding))
    )
    conn.commit()
    cursor.close()
    conn.close()

def attendance_log(employee_id, camera_name, direction):
    conn = get_db()
    cursor = conn.cursor()
    sql = "INSERT INTO attendance_logs (employee_id, camera_name, direction, timestamp) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (employee_id, camera_name, direction, datetime.now()))
    conn.commit()
    cursor.close()
    conn.close()

# ---------- GET ALL EMPLOYEES ----------
def get_all_employees():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, embedding FROM employees")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows