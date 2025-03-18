import mysql.connector
import json

db_config = {
    'user': 'root',
    'password': 'Pvk@14827',
    'host': 'localhost',
    'database': 'moodle',
    'port': 3307
}

# Read data from JSON file
with open("student_performance.json", "r") as f:
    data = json.load(f)

try:
    print("Connecting...")
    conn = mysql.connector.connect(**db_config)
    print("Connected!")

    cursor = conn.cursor()

    # Step 1: DELETE old data
    delete_query = "DELETE FROM mdl_gradereport_userperformance_data"
    cursor.execute(delete_query)
    conn.commit()
    print("Old data cleared from the table.")

    # Step 2: Insert fresh data
    insert_query = """
        INSERT INTO mdl_gradereport_userperformance_data (userid, courseid, performance, lastupdated)
        VALUES (%s, %s, %s, NOW())
        """
    for student in data:
        cursor.execute(insert_query, (student["user_id"], student["course_id"], student["Performance"]))
    
    conn.commit()
    print("New performance data inserted successfully.")

    conn.close()
except mysql.connector.Error as err:
    print(f"Database Error: {err}")
