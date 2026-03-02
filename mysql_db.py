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

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # CREATE EMPLOYEES TABLE
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                embedding LONGTEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
    """)

    # CREATE ATTENDANCE_LOGS TABLE
    cursor.execute("""
           CREATE TABLE IF NOT EXISTS attendance_logs (
               id INT AUTO_INCREMENT PRIMARY KEY,
               employee_id INT NOT NULL,
               camera_name VARCHAR(100) NOT NULL,
               direction ENUM('IN', 'OUT') NOT NULL,
               timestamp DATETIME NOT NULL,
               FOREIGN KEY (employee_id) REFERENCES employees(id)
                   ON DELETE CASCADE
           )
    """)

    conn.commit()
    cursor.close()
    conn.close()

# INSERT EMPLOYEE
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

# GET ALL EMPLOYEES
def get_all_employees():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, embedding FROM employees")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows

if __name__ == "__main__":
    init_db()