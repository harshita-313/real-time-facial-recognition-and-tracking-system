import os
import numpy as np
from deepface import DeepFace
from mysql_db import insert_employee

# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def register_all_employees():

    base_folder = "employees"
    for employee_name in os.listdir(base_folder):
        employee_folder = os.path.join(base_folder, employee_name)
        if not os.path.isdir(employee_folder):
            continue

        # CHECK IF EMPLOYEE ALREADY EXISTS
        from mysql_db import get_db
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM employees WHERE name = %s", (employee_name,))
        existing = cursor.fetchone()
        cursor.close()
        conn.close()

        if existing:
            print(f"⚠ {employee_name} already exists in database — Skipping")
            continue

        print(f"\nProcessing: {employee_name}")

        embeddings = []

        for file in os.listdir(employee_folder):
            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                img_path = os.path.join(employee_folder, file)
                try:
                    result = DeepFace.represent(
                        img_path=img_path,
                        model_name="ArcFace",
                        enforce_detection=False
                    )
                    embedding = result[0]["embedding"]
                    embeddings.append(embedding)
                    print(f"✔ Processed {file}")
                except Exception as e:
                    print(f"✖ Error processing {file} -> {e}")

        if len(embeddings) == 0:
            print("❌ No valid faces — skipping")
            continue

        # Average embeddings
        avg_embedding = np.mean(embeddings, axis=0)

        # Store in DB
        insert_employee(employee_name, avg_embedding.tolist())
        print(f"✅ Saved {employee_name} to database")


if __name__ == "__main__":
    register_all_employees()