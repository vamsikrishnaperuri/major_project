import requests
import json
import csv
import io
import ezodf  # For ODS creation

def get_moodle_grades(moodle_url, token, course_id, user_id=None, output_format="ods", output_file="grades"):
    """
    Retrieves grade data from Moodle using a web service token and saves it to a file.

    Args:
        moodle_url: Your Moodle site's URL (e.g., "https://yourmoodlesite.com").
        token: Your Moodle web service token.
        course_id: The ID of the course.
        user_id: (Optional) The ID of the user. If None, retrieves grades for all users in the course.
        output_format: Output format ('ods', 'json', or 'csv').
        output_file: Base name of the output file.
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

        if output_format == "json":
            with open(f"{output_file}.json", "w") as outfile:
                json.dump(data, outfile, indent=4)
            print(f"Data exported to {output_file}.json")

        elif output_format == "csv":
            # Extract data from the JSON
            table_data = data.get('tables', [])
            if table_data:
                rows = table_data[0].get('tabledata', [])
                if rows:
                    with open(f"{output_file}.csv", "w", newline='', encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile)
                        header = [cell.get('header', '') for cell in rows[0]]
                        writer.writerow(header)
                        for row in rows[1:]: #skip the header
                            writer.writerow([cell.get('text', '') for cell in row])
                    print(f"Data exported to {output_file}.csv")
                else:
                    print("No table data found in the response.")
            else:
                 print("No table found in response.")

        elif output_format == "ods":
            table_data = data.get('tables', [])
            if table_data:
                rows = table_data[0].get('tabledata', [])
                if rows:
                    doc = ezodf.newdoc(doctype='ods', filename=f"{output_file}.ods")
                    sheet = doc.sheets[0]
                    for row_index, row in enumerate(rows):
                        for col_index, cell in enumerate(row):
                            sheet[row_index, col_index].set_value(cell.get('text', cell.get('header','')))
                    doc.save()
                    print(f"Data exported to {output_file}.ods")
                else:
                    print("No table data found in the response.")
            else:
                print("No table found in response.")

        else:
            print("Invalid output format. Choose 'json', 'csv', or 'ods'.")

        return data

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

# Example usage:
moodle_url = "http://localhost"
token = "ddf40222bac1d5f4240bdd8c45a2e01d"
course_id = 2

grades = get_moodle_grades(moodle_url, token, course_id, output_format="ods") #changed to ods.