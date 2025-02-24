import requests
import json
import re
import pandas as pd
from sklearn.cluster import KMeans
import json

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

def categorize_students_json(input_json):
    """
    Categorizes students based on their final grades from JSON input.

    Args:
        input_json (list): A list of dictionaries, where each dictionary represents a student.

    Returns:
        list: A list of dictionaries, where each dictionary contains user_id and performance category.
    """
    try:
        data = pd.DataFrame(input_json)
        data['finalgrade'] = pd.to_numeric(data['finalgrade'], errors='coerce') #convert finalgrade to numeric.
        data = data.dropna(subset=['finalgrade'])

        marks = data[['finalgrade']].values

        kmeans = KMeans(n_clusters=3, random_state=42)
        data['Category'] = kmeans.fit_predict(marks)

        centers = kmeans.cluster_centers_.flatten()
        sorted_indices = centers.argsort()
        category_map = {sorted_indices[0]: 'Poor Performance',
                            sorted_indices[1]: 'Average Performance',
                            sorted_indices[2]: 'Good Performance'}

        data['Performance'] = data['Category'].map(category_map)

        result = data[['user_id', 'Performance']].to_dict(orient='records')
        return result

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# Example usage:
moodle_url = "http://localhost"
token = "ddf40222bac1d5f4240bdd8c45a2e01d"
course_id = 2

grades = get_moodle_grades(moodle_url, token, course_id)

# input_json = [
#     {
#         "user_id": 4,
#         "firstname": "v",
#         "lastname": "2",
#         "course_shortname": "SFD2025",
#         "itemname": [
#             "Assignment",
#             "Quiz",
#             "Assignment"
#         ],
#         "finalgrade": "180.5"
#     },
#     {
#         "user_id": 5,
#         "firstname": "v",
#         "lastname": "3",
#         "course_shortname": "SFD2025",
#         "itemname": [
#             "Assignment",
#             "Quiz",
#             "Assignment"
#         ],
#         "finalgrade": "140.0"
#     },
#     {
#         "user_id": 6,
#         "firstname": "v",
#         "lastname": "4",
#         "course_shortname": "SFD2025",
#         "itemname": [
#             "Assignment",
#             "Quiz",
#             "Assignment"
#         ],
#         "finalgrade": "120.0"
#     },
#     {
#         "user_id": 3,
#         "firstname": "Peruri",
#         "lastname": "Vamsi Krishna",
#         "course_shortname": "SFD2025",
#         "itemname": [
#             "Assignment",
#             "Assignment"
#         ],
#         "finalgrade": "97.0"
#     }
# ]

output_json = categorize_students_json(grades)
print(json.dumps(output_json, indent=4))