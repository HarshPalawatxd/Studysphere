 # exams.py - Exam tracker for StudySphere
from datetime import datetime
from storage import load_data, save_data

FILE_NAME = "exams.json"
DATE_FORMAT = "%d-%m-%Y"


def get_all_exams():
    exams = load_data(FILE_NAME)
    return exams if isinstance(exams, list) else []


def get_user_exams(exams, current_user):
    """Return only the exams that belong to current_user."""
    return [e for e in exams if e.get("user") == current_user]


def generate_new_id(exams):
    max_id = 0
    for e in exams:
        if e.get("id", 0) > max_id:
            max_id = e["id"]
    return max_id + 1


def add_exam(current_user):
    print("\n--- Add Exam ---")
    subject = input("Subject: ").strip()
    date_text = input("Exam date (DD-MM-YYYY): ").strip()

    if not subject or not date_text:
        print("Error: All fields are required.")
        return

    try:
        datetime.strptime(date_text, DATE_FORMAT)
    except ValueError:
        print("Invalid date. Use DD-MM-YYYY (example: 25-12-2026).")
        return

    exams = get_all_exams()
    new_exam = {
        "id": generate_new_id(exams),
        "subject": subject,
        "date": date_text,
        "user": current_user,
    }
    exams.append(new_exam)
    save_data(FILE_NAME, exams)
    print(f"Exam added! (ID: {new_exam['id']})")


def view_exams(current_user):
    print("\n--- My Exams ---")
    my_exams = get_user_exams(get_all_exams(), current_user)
    if not my_exams:
        print("No exams added yet.")
        return

    my_exams.sort(key=lambda e: datetime.strptime(e["date"], DATE_FORMAT))
    today = datetime.now().date()

    for e in my_exams:
        exam_date = datetime.strptime(e["date"], DATE_FORMAT).date()
        days_left = (exam_date - today).days
        if days_left > 0:
            note = f"{days_left} day(s) left"
        elif days_left == 0:
            note = "Today!"
        else:
            note = "Completed"
        print(f"[{e['id']}] {e['subject']} - {e['date']} ({note})")


def delete_exam(current_user):
    print("\n--- Delete Exam ---")
    exams = get_all_exams()
    my_exams = get_user_exams(exams, current_user)
    if not my_exams:
        print("You have no exams to delete.")
        return

    for e in my_exams:
        print(f"[{e['id']}] {e['subject']} - {e['date']}")

    exam_id = input("Enter exam ID to delete: ").strip()
    if not exam_id.isdigit():
        print("Invalid ID.")
        return

    target = int(exam_id)
    if not any(e["id"] == target for e in my_exams):
        print("No exam found with that ID under your account.")
        return

    updated = [e for e in exams if e["id"] != target]
    save_data(FILE_NAME, updated)
    print("Exam deleted.")


def exams_menu(current_user):
    while True:
        print("\n===============================")
        print("  StudySphere - Exam Tracker")
        print(f"  Logged in as: {current_user}")
        print("===============================")
        print("1. Add exam")
        print("2. View my exams")
        print("3. Delete exam")
        print("4. Back")

        choice = input("Enter choice (1-4): ").strip()

        if choice == "1":
            add_exam(current_user)
        elif choice == "2":
            view_exams(current_user)
        elif choice == "3":
            delete_exam(current_user)
        elif choice == "4":
            print("Returning to main menu...")
            break
        else:
            print("Invalid selection. Please choose between 1 and 4.")