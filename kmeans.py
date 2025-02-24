import pandas as pd
from sklearn.cluster import KMeans
import json

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

# Example usage with your provided JSON:
input_json = [
    {
        "user_id": 4,
        "firstname": "v",
        "lastname": "2",
        "course_shortname": "SFD2025",
        "itemname": [
            "Assignment",
            "Quiz",
            "Assignment"
        ],
        "finalgrade": "180.5"
    },
    {
        "user_id": 5,
        "firstname": "v",
        "lastname": "3",
        "course_shortname": "SFD2025",
        "itemname": [
            "Assignment",
            "Quiz",
            "Assignment"
        ],
        "finalgrade": "140.0"
    },
    {
        "user_id": 6,
        "firstname": "v",
        "lastname": "4",
        "course_shortname": "SFD2025",
        "itemname": [
            "Assignment",
            "Quiz",
            "Assignment"
        ],
        "finalgrade": "120.0"
    },
    {
        "user_id": 3,
        "firstname": "Peruri",
        "lastname": "Vamsi Krishna",
        "course_shortname": "SFD2025",
        "itemname": [
            "Assignment",
            "Assignment"
        ],
        "finalgrade": "97.0"
    }
]

output_json = categorize_students_json(input_json)
print(json.dumps(output_json, indent=4))