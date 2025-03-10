import requests
import re
import json

import requests
import re
import json

def get_all_users_moodle_grades(moodle_url, token):
    """
    Retrieves grades for all users in all courses in Moodle, grouped by course.
    Excludes course ID = 1 and users whose name contains 'Admin' (case-insensitive).
    
    :param moodle_url: Base URL of the Moodle instance
    :param token: API Token for authentication
    :return: Dictionary of courses with user grades
    """
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





# Example usage:
moodle_url = "http://localhost"
token = "TOKEN"
# course_id = 2

grades = get_all_users_moodle_grades(moodle_url, token)



