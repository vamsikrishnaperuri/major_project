import requests
import json
import re
import pandas as pd
from sklearn.cluster import KMeans

def get_all_users_moodle_grades(moodle_url, token):
    try:
        courses_response = requests.post(
            f"{moodle_url}/webservice/rest/server.php",
            data={
                "wstoken": token,
                "wsfunction": "core_course_get_courses",
                "moodlewsrestformat": "json"
            }
        )
        courses_response.raise_for_status()
        courses = courses_response.json()

        if not isinstance(courses, list):
            print("Error: Moodle API returned unexpected data:", courses)
            return {}

        all_courses_data = {}

        for course in courses:
            course_id = course.get("id")
            if course_id == 1:
                continue

            course_shortname = course.get("shortname", f"Course-{course_id}")

            users_response = requests.post(
                f"{moodle_url}/webservice/rest/server.php",
                data={
                    "wstoken": token,
                    "wsfunction": "core_enrol_get_enrolled_users",
                    "moodlewsrestformat": "json",
                    "courseid": course_id
                }
            )
            users_response.raise_for_status()
            users = users_response.json()

            if not isinstance(users, list):
                print(f"Error fetching users for course {course_id}:", users)
                continue

            all_courses_data[course_id] = {
                "course_id": course_id,
                "course_shortname": course_shortname,
                "users": []
            }

            for user in users:
                user_id = user.get("id")
                user_fullname = user.get("fullname", "")

                if "admin" in user_fullname.lower():
                    continue

                names = user_fullname.split(" ")
                firstname = names[0] if names else ""
                lastname = " ".join(names[1:]) if len(names) > 1 else ""

                grades_response = requests.post(
                    f"{moodle_url}/webservice/rest/server.php",
                    data={
                        "wstoken": token,
                        "wsfunction": "gradereport_user_get_grades_table",
                        "moodlewsrestformat": "json",
                        "courseid": course_id,
                        "userid": user_id
                    }
                )
                grades_response.raise_for_status()
                grades_data = grades_response.json()

                if not grades_data.get("tables"):
                    continue

                user_data = {
                    "user_id": user_id,
                    "firstname": firstname,
                    "lastname": lastname,
                    "grades": [],
                    "total_finalgrade": 0
                }

                for table in grades_data["tables"]:
                    if table.get("userid") != user_id:
                        continue

                    for row in table.get("tabledata", []):
                        if "grade" in row and "itemname" in row:
                            if isinstance(row["grade"], dict) and isinstance(row["itemname"], dict):
                                itemname_content = row["itemname"].get("content", "").strip()

                                itemname_match = re.search(r'title="(.*?)"', itemname_content)
                                itemname = itemname_match.group(1) if itemname_match else None

                                grade_content = row["grade"].get("content", "").strip()
                                grade_match = re.search(r'(\d+\.?\d*)', grade_content)
                                finalgrade = float(grade_match.group(1)) if grade_match else None

                                if finalgrade is not None and itemname is not None and "Natural" not in itemname:
                                    user_data["grades"].append({
                                        "itemname": itemname,
                                        "finalgrade": finalgrade
                                    })

                user_data["total_finalgrade"] = sum(g["finalgrade"] for g in user_data["grades"])

                if user_data["grades"]:
                    all_courses_data[course_id]["users"].append(user_data)

        return all_courses_data

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def categorize_students_json(input_json):
    try:
        categorized_students = []

        for course_id, course_data in input_json.items():
            students = []

            for user in course_data.get("users", []):
                students.append({
                    "user_id": user["user_id"],
                    "course_id": course_id,
                    "total_finalgrade": user["total_finalgrade"]
                })

            data = pd.DataFrame(students)

            if len(data) < 3:
                for user in students:
                    categorized_students.append({
                        "user_id": user["user_id"],
                        "course_id": course_id,
                        "Performance": "Not Enough Data"
                    })
                continue

            data = data.dropna(subset=['total_finalgrade'])
            marks = data[['total_finalgrade']].values
            kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
            data['Category'] = kmeans.fit_predict(marks)

            centers = kmeans.cluster_centers_.flatten()
            sorted_indices = centers.argsort()
            category_map = {
                sorted_indices[0]: 'Poor Performance',
                sorted_indices[1]: 'Average Performance',
                sorted_indices[2]: 'Good Performance'
            }

            data['Performance'] = data['Category'].map(category_map)
            categorized_students.extend(data[['user_id', 'course_id', 'Performance']].to_dict(orient='records'))

        return categorized_students

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# --- MAIN EXECUTION ---

moodle_url = "http://localhost"
token = "fb02494ebe9accf818808979db008242"

grades = get_all_users_moodle_grades(moodle_url, token)
output_json = categorize_students_json(grades)

# Save to JSON file (Overwrite every time)
output_file = "student_performance.json"
with open(output_file, "w") as f:
    json.dump(output_json, f, indent=4)

print(f"Categorized student performance saved to {output_file}")
