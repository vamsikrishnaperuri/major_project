import mysql.connector

db_config = {
    'user': 'root',
    'password': 'Pvk@14827',
    'host': 'localhost',
    'database': 'moodle',
    'port': 3307
}

data = [
    {
        "user_id": 3,
        "course_id": 2,
        "Performance": "Average Performance"
    },
    {
        "user_id": 4,
        "course_id": 2,
        "Performance": "Poor Performance"
    },
    {
        "user_id": 5,
        "course_id": 2,
        "Performance": "Good Performance"
    },
    {
        "user_id": 3,
        "course_id": 3,
        "Performance": "Good Performance"
    },
    {
        "user_id": 4,
        "course_id": 3,
        "Performance": "Poor Performance"
    },
    {
        "user_id": 5,
        "course_id": 3,
        "Performance": "Average Performance"
    }
]

try:
    print("Connecting...")
    print(f"DB Config: {db_config}")
    conn = mysql.connector.connect(**db_config)
    print("Connected!")
    cursor = conn.cursor()
    print("Connected to the database")
    insert_query = """
        INSERT INTO mdl_gradereport_userperformance_data (userid, courseid, performance, lastupdated)
        VALUES (%s, %s, %s, NOW())
        """
    for student in data:
        cursor.execute(insert_query, (student["user_id"], student["course_id"], student["Performance"]))
        conn.commit()

    print("Performance data updated successfully.")
    conn.close()
except mysql.connector.Error as err:
    print(f"Connection Error: {err}")
