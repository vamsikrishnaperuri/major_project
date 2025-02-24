import mysql.connector
import json

def extract_grades(host, user, password, database, course_id, output_format="json", output_file="grades"):
    """
    Extracts grade data from a Moodle database and saves it to a file.

    Args:
        host: Database host.
        user: Database user.
        password: Database password.
        database: Database name.
        course_id: Course ID to filter by.
        output_format: Output format ('json' or 'csv').
        output_file: Base name of the output file.
    """
    try:
        mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
        )
        mycursor = mydb.cursor(dictionary=True)

        query = """
            SELECT
                u.id AS user_id,
                u.firstname,
                u.lastname,
                c.shortname AS course_shortname,
                gi.itemname,
                gg.finalgrade
            FROM
                mdl_grade_grades gg
            JOIN
                mdl_grade_items gi ON gg.itemid = gi.id
            JOIN
                mdl_user u ON gg.userid = u.id
            JOIN
                mdl_course c ON gi.courseid = c.id
            WHERE
                gi.courseid = %s AND gi.itemtype != 'course';
        """

        mycursor.execute(query, (course_id,))
        results = mycursor.fetchall()

        if output_format == "json":
            with open(f"{output_file}.json", "w") as outfile:
                json.dump(results, outfile, indent=4)
            print(f"Data exported to {output_file}.json")
        elif output_format == "csv":
            import csv
            with open(f"{output_file}.csv", "w", newline='', encoding='utf-8') as csvfile:
                fieldnames = results[0].keys() if results else []
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in results:
                    writer.writerow(row)
            print(f"Data exported to {output_file}.csv")
        else:
            print("Invalid output format. Choose 'json' or 'csv'.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'mydb' in locals() and mydb.is_connected():
            mycursor.close()
            mydb.close()

# Example usage:
extract_grades(
    host="localhost",
    user="root",
    password="Pvk@14827",
    database="moodle",
    course_id=2,
    output_format="csv", #or "json"
    output_file="course2_grades"
)