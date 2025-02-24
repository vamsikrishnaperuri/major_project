import requests
import json
import re

def get_moodle_grades(moodle_url, token, course_id, user_id=None):
    """
    Retrieves grade data from Moodle and formats it like the SQL query output.
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
                user_fullname = table.get('userfullname')
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
                                grade_content = row['grade'].get('content', '')
                                itemname_content = row['itemname'].get('content', '')

                                grade_match = re.search(r'>([\d.]+)', grade_content)
                                finalgrade = grade_match.group(1) if grade_match else None

                                itemname_match = re.search(r'title="(.*?)"', itemname_content)
                                itemname = itemname_match.group(1) if itemname_match else None

                                if finalgrade is not None and itemname is not None and course_shortname is not None:
                                    if user_id not in grade_items_by_user:
                                        grade_items_by_user[user_id] = {"itemnames": [], "finalgrades": [], "firstname": firstname, "lastname": lastname, "course_shortname":course_shortname}
                                    grade_items_by_user[user_id]["itemnames"].append(itemname)
                                    grade_items_by_user[user_id]["finalgrades"].append(float(finalgrade))

            for user_id, user_data in grade_items_by_user.items():
                total_grade = sum(user_data["finalgrades"])
                extracted_data.append({
                    "user_id": user_id,
                    "firstname": user_data["firstname"],
                    "lastname": user_data["lastname"],
                    "course_shortname": user_data["course_shortname"],
                    "itemname": user_data["itemnames"],
                    "finalgrade": str(total_grade)
                })

        print(json.dumps(extracted_data, indent=4))
        return extracted_data

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# Example usage:
moodle_url = "http://localhost"
token = "ddf40222bac1d5f4240bdd8c45a2e01d"
course_id = 2

grades = get_moodle_grades(moodle_url, token, course_id)