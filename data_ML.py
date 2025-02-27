import requests
import json
import re
import pandas as pd
from sklearn.cluster import KMeans
import json

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
                                itemname_content = row['itemname'].get('content', '').strip()
                                
                                # Extract item name properly
                                itemname_match = re.search(r'title="(.*?)"', itemname_content)
                                itemname = itemname_match.group(1) if itemname_match else None

                                # Extract numeric grade (handles both plain numbers and wrapped inside <div>)
                                grade_content = row['grade'].get('content', '').strip()
                                grade_match = re.search(r'(\d+\.?\d*)', grade_content)  # Extracts first valid number
                                finalgrade = float(grade_match.group(1)) if grade_match else None

                                # Ensure valid data and exclude "Natural"
                                if finalgrade is not None and itemname is not None and course_shortname is not None and "Natural" not in itemname:
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

            # Calculate total final grade for each user
            for user_id, user_data in grade_items_by_user.items():
                total_finalgrade = sum(g["finalgrade"] for g in user_data["grades"])  # Sum up all grades
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

def categorize_students_json(input_json):
    """
    Categorizes students based on their total final grades from JSON input.

    Args:
        input_json (list): A list of dictionaries, each representing a student's data.

    Returns:
        list: A list of dictionaries with user_id, courseid, and performance category.
    """
    try:
        # Convert JSON to DataFrame
        data = pd.DataFrame(input_json)

        # Extract and sum all grades per student
        data['finalgrade'] = data['grades'].apply(lambda x: sum([g['finalgrade'] for g in x]) if isinstance(x, list) else 0)

        # Drop missing or invalid final grades
        data = data.dropna(subset=['finalgrade'])

        # Prepare for KMeans
        marks = data[['finalgrade']].values

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

        # Format Output JSON
        result = data[['user_id', 'course_shortname', 'Performance']].rename(columns={'course_shortname': 'courseid'}).to_dict(orient='records')
        
        return result

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# Example usage:
moodle_url = "http://localhost"
token = "fb02494ebe9accf818808979db008242"
course_id = 3

grades = get_moodle_grades(moodle_url, token, course_id)

# [
#     {
#         "user_id": 3,
#         "firstname": "v",
#         "lastname": "1",
#         "course_shortname": "FreedomFest25",
#         "grades": [
#             {
#                 "itemname": "Assignment",
#                 "finalgrade": 70.0
#             }
#         ],
#         "total_finalgrade": 70.0
#     },
#     {
#         "user_id": 4,
#         "firstname": "v",
#         "lastname": "2",
#         "course_shortname": "FreedomFest25",
#         "grades": [
#             {
#                 "itemname": "Assignment",
#                 "finalgrade": 60.0
#             }
#         ],
#         "total_finalgrade": 60.0
#     },
#     {
#         "user_id": 5,
#         "firstname": "v",
#         "lastname": "3",
#         "course_shortname": "FreedomFest25",
#         "grades": [
#             {
#                 "itemname": "Assignment",
#                 "finalgrade": 90.0
#             }
#         ],
#         "total_finalgrade": 90.0
#     }
# ]

output_json = categorize_students_json(grades)
print(json.dumps(output_json, indent=4))