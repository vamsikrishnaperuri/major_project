import requests
import json
import re
import pandas as pd
from sklearn.cluster import KMeans

def get_all_users_moodle_grades(moodle_url, token):

    try:
        # Step 1: Get the list of all courses
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

        # Step 2: Loop through each course (excluding course ID 1)
        for course in courses:
            course_id = course.get("id")

            if course_id == 1:  # Exclude site-wide course
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

            # Step 3: Fetch grades for each user (excluding users with "Admin" in their name)
            for user in users:
                user_id = user.get("id")
                user_fullname = user.get("fullname", "")

                if "admin" in user_fullname.lower():  # Case-insensitive check for "admin"
                    continue  # Skip admin users

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
                    continue  # Skip if no grade data

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

                                # Extract item name
                                itemname_match = re.search(r'title="(.*?)"', itemname_content)
                                itemname = itemname_match.group(1) if itemname_match else None

                                # Extract numeric grade (handling nested divs)
                                grade_content = row["grade"].get("content", "").strip()
                                grade_match = re.search(r'(\d+\.?\d*)', grade_content)  # Extracts first valid number
                                finalgrade = float(grade_match.group(1)) if grade_match else None

                                # Exclude "Natural" grades
                                if finalgrade is not None and itemname is not None and "Natural" not in itemname:
                                    user_data["grades"].append({
                                        "itemname": itemname,
                                        "finalgrade": finalgrade
                                    })

                # Calculate total final grade
                user_data["total_finalgrade"] = sum(g["finalgrade"] for g in user_data["grades"])

                if user_data["grades"]:  # Only add if user has grades
                    all_courses_data[course_id]["users"].append(user_data)

        print(json.dumps(all_courses_data, indent=4))
        return all_courses_data

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


def categorize_students_json(input_json):

    try:
        categorized_students = []

        # Process each course separately
        for course_id, course_data in input_json.items():
            students = []

            for user in course_data.get("users", []):
                students.append({
                    "user_id": user["user_id"],
                    "course_id": course_id,
                    "total_finalgrade": user["total_finalgrade"]
                })

            # Convert to DataFrame
            data = pd.DataFrame(students)

            # Skip courses with less than 3 students (KMeans requires at least 3 clusters)
            if len(data) < 3:
                for user in students:
                    categorized_students.append({
                        "user_id": user["user_id"],
                        "course_id": course_id,
                        "Performance": "Not Enough Data"
                    })
                continue

            # Drop missing or invalid final grades
            data = data.dropna(subset=['total_finalgrade'])

            # Prepare for KMeans
            marks = data[['total_finalgrade']].values

            # Apply KMeans Clustering
            kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
            data['Category'] = kmeans.fit_predict(marks)

            # Map Categories to Performance Labels
            centers = kmeans.cluster_centers_.flatten()
            sorted_indices = centers.argsort()
            category_map = {
                sorted_indices[0]: 'Poor Performance',
                sorted_indices[1]: 'Average Performance',
                sorted_indices[2]: 'Good Performance'
            }

            data['Performance'] = data['Category'].map(category_map)

            # Append results for this course
            categorized_students.extend(data[['user_id', 'course_id', 'Performance']].to_dict(orient='records'))

        return categorized_students

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

moodle_url = "http://localhost"
token = "fb02494ebe9accf818808979db008242"
# course_id = 2

grades = get_all_users_moodle_grades(moodle_url, token)


output_json = categorize_students_json(grades)
print(json.dumps(output_json, indent=4))
