import requests
import pandas as pd
from sklearn.cluster import KMeans

# ✅ Moodle API Details (Update these)
MOODLE_URL = "http://localhost/moodle/webservice/rest/server.php"
TOKEN = "ddf40222bac1d5f4240bdd8c45a2e01d"  # Replace with your actual token
COURSE_ID = "2"  # Replace with your Moodle course ID

# ✅ Paths for processing ODS files
TEMP_GRADE_FILE = "temp_grades.ods"
TEMP_UPDATED_FILE = "categorized_students.ods"

# ✅ Function to Fetch Grades via API
def fetch_grades():
    params = {
        "wstoken": TOKEN,
        "wsfunction": "gradereport_user_get_grades_table",
        "moodlewsrestformat": "json",
        "courseid": COURSE_ID
    }
    
    response = requests.get(MOODLE_URL, params=params)
    grades = response.json()

    # Convert JSON data into a DataFrame
    df = pd.DataFrame(grades['tables'][0]['tabledata'])
    
    # Save it as an ODS file for ML processing
    df.to_excel(TEMP_GRADE_FILE, engine="odf", index=False)
    print(f"✅ Grades fetched and saved as ODS: {TEMP_GRADE_FILE}")
    
    return df

# ✅ Function to Process Grades using ML (on ODS file)
def categorize_students():
    # Load the ODS file for processing
    data = pd.read_excel(TEMP_GRADE_FILE, engine="odf")

    marks_column = 'Course total (Real)'  # Ensure this matches Moodle's response
    data = data.dropna(subset=[marks_column])  # Remove empty values

    # Extract marks for clustering
    marks = data[[marks_column]].values

    # Apply KMeans Clustering
    kmeans = KMeans(n_clusters=3, random_state=42)
    data['Category'] = kmeans.fit_predict(marks)

    # Map clusters to performance categories
    centers = kmeans.cluster_centers_.flatten()
    sorted_indices = centers.argsort()
    category_map = {
        sorted_indices[0]: 'Poor Performance',
        sorted_indices[1]: 'Average Performance',
        sorted_indices[2]: 'Good Performance'
    }
    data['Performance'] = data['Category'].map(category_map)

    # Drop cluster column
    data = data.drop(columns=['Category'])

    # Save categorized data back as ODS
    data.to_excel(TEMP_UPDATED_FILE, engine="odf", index=False)
    print(f"✅ Students categorized and saved as ODS: {TEMP_UPDATED_FILE}")
    
    return data

# ✅ Function to Upload Updated Grades via API
def upload_grades(df):
    # Convert DataFrame to Moodle API-compatible format
    grade_data = []
    for _, row in df.iterrows():
        grade_data.append({
            "userid": row["userid"],  # Adjust based on actual API response
            "grade": row["Performance"]
        })

    payload = {
        "wstoken": TOKEN,
        "wsfunction": "gradereport_import",
        "moodlewsrestformat": "json",
        "grades": grade_data
    }

    response = requests.post(MOODLE_URL, data=payload)
    print("✅ Updated grades uploaded to Moodle API!", response.text)

# ✅ Run Full Workflow
if __name__ == "__main__":
    fetch_grades()  # Step 1: Fetch and save ODS
    df = categorize_students()  # Step 2: Process ODS with ML
    upload_grades(df)  # Step 3: Upload back to Moodle
