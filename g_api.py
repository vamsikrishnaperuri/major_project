import requests
import json
import re

def get_moodle_grades(moodle_url, token, course_id, user_id=None):
    """
    Retrieves grade data from Moodle and formats it correctly,
    excluding entries with itemname "Natural".
    """
    function_name = "gradereport_user_get_grades_table"
    params = {
        "wstoken": token,
        "wsfunction": function_name,
        "moodlewsrestformat": "json",
        "courseid": course_id,
    }

    if user_id:
        params["userid"] = user_id

    try:
        response = requests.post(f"{moodle_url}/webservice/rest/server.php", data=params)
        response.raise_for_status()
        data = response.json()

        extracted_data = []
        if data.get('tables'):
            grade_items_by_user = {}
            for table in data['tables']:
                user_id = table.get('userid')
                user_fullname = table.get('userfullname', '')
                names = user_fullname.split(" ")
                firstname = names[0] if names else ""
                lastname = " ".join(names[1:]) if len(names) > 1 else ""

                # Extract course_shortname from the first row of tabledata
                if table.get('tabledata') and 'content' in table['tabledata'][0]['itemname']:
                    course_shortname_match = re.search(r'<span>(.*?)</span>', table['tabledata'][0]['itemname']['content'])
                    course_shortname = course_shortname_match.group(1) if course_shortname_match else None
                else:
                    course_shortname = None

                if table.get('tabledata'):
                    for row in table['tabledata']:
                        if 'grade' in row and 'itemname' in row:
                            if isinstance(row['grade'], dict) and isinstance(row['itemname'], dict):
                                grade_content = row['grade'].get('content', '').strip()
                                itemname_content = row['itemname'].get('content', '').strip()

                                # Extracting numeric grade directly
                                finalgrade = None
                                if grade_content.replace('.', '', 1).isdigit():  # Handles float numbers like "90.00"
                                    finalgrade = float(grade_content)

                                # Extract item name properly
                                itemname_match = re.search(r'title="(.*?)"', itemname_content)
                                itemname = itemname_match.group(1) if itemname_match else None

                                # Exclude "Natural" from results
                                if finalgrade is not None and itemname is not None and course_shortname is not None and itemname != "Natural":
                                    if user_id not in grade_items_by_user:
                                        grade_items_by_user[user_id] = {
                                            "firstname": firstname,
                                            "lastname": lastname,
                                            "course_shortname": course_shortname,
                                            "grades": []
                                        }
                                    grade_items_by_user[user_id]["grades"].append({
                                        "itemname": itemname,
                                        "finalgrade": finalgrade
                                    })

            for user_id, user_data in grade_items_by_user.items():
                total_finalgrade = sum(g["finalgrade"] for g in user_data["grades"])  # Summing grades
                extracted_data.append({
                    "user_id": user_id,
                    "firstname": user_data["firstname"],
                    "lastname": user_data["lastname"],
                    "course_shortname": user_data["course_shortname"],
                    "grades": user_data["grades"],
                    "total_finalgrade": total_finalgrade
                })

        print(json.dumps(extracted_data, indent=4))
        return extracted_data

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


# Example usage:
moodle_url = "http://localhost"
token = "YOUR_TOKEN"
course_id = 2

grades = get_moodle_grades(moodle_url, token, course_id)



