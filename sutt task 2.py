import pandas as pd
import json
import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


file_path = "/Users/apple/Downloads/Timetable Workbook - SUTT Task 1.xlsx"


def parse_workbook(file_path):
    try:
        workbook = pd.ExcelFile(file_path)
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return None
    except Exception as e:
        logging.error(f"An error occurred while loading the workbook: {e}")
        return None

    all_courses = []

    for sheet_name in workbook.sheet_names:
        logging.info(f"Parsing sheet: {sheet_name}")
        df = pd.read_excel(workbook, sheet_name=sheet_name)
        
        
        course_code = df.iloc[0, 1]
        course_title = df.iloc[1, 1]
        credit_structure = df.iloc[2, 1]

        sections = []
        for index, row in df.iterrows():
            if index < 4:  
                continue

            section = {
                "section_type": row["Section Type"],
                "section_number": row["Section Number"],
                "instructor": row["Instructor"],
                "room_number": row["Room Number"],
                "time_slots": [int(slot) for slot in str(row["Time Slot"]).split(",") if slot.isdigit()]
            }
            sections.append(section)

        course_data = {
            "course_code": course_code,
            "course_title": course_title,
            "credits": credit_structure,
            "sections": sections
        }
        
        all_courses.append(course_data)

    return all_courses

def convert_time_slots(slots):
    """
    Convert numeric time slots to readable format (e.g., 1 -> "8-9", 2 -> "9-10").
    """
    time_mapping = {
        1: "8-9", 2: "9-10", 3: "10-11", 4: "11-12",
        5: "12-1", 6: "1-2", 7: "2-3", 8: "3-4", 9: "4-5"
    }
    return [time_mapping.get(slot, "Unknown") for slot in slots]

def generate_json(course_data):
    
    for course in course_data:
        for section in course["sections"]:
            section["time_slots"] = convert_time_slots(section["time_slots"])

    
    output_file = "timetable.json"
    with open(output_file, "w") as json_file:
        json.dump({"courses": course_data}, json_file, indent=4)
    logging.info(f"JSON file generated: {output_file}")

def main():
    logging.info("Starting timetable parsing and JSON generation...")
    course_data = parse_workbook(file_path)
    if course_data:
        generate_json(course_data)
        logging.info("Task completed successfully.")
    else:
        logging.error("Failed to parse workbook.")

if __name__ == "__main__":
    main()
