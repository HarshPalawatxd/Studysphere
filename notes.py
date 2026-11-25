# notes.py - Handles note management in the StudySphere console platform

from storage import load_data, save_data

NOTES_FILE = "notes.json"


def get_all_notes():
    """
    Loads all notes from the storage file.
    Returns a list of note dictionaries.
    """
    notes = load_data(NOTES_FILE)
    # Ensure we return a list even if the file is empty or None
    if not isinstance(notes, list):
        return []
    return notes


def generate_new_id(notes):
    """
    Generates a unique incremental ID based on existing notes.
    """
    if not notes:
        return 1
    # Find the maximum existing ID and increment by 1
    max_id = 0
    for note in notes:
        if note.get("id", 0) > max_id:
            max_id = note["id"]
    return max_id + 1


def add_note(current_user):
    """
    Prompts the logged-in user for subject, title, and content,
    creates a new note dictionary, and saves it.
    """
    print("\n--- Add New Note ---")
    subject = input("Enter subject (e.g., Physics, History): ").strip()
    title = input("Enter title: ").strip()
    content = input("Enter content: ").strip()

    # Simple input validation
    if not subject or not title or not content:
        print("Error: All fields are required. Note not added.")
        return

    # Load current notes
    notes = get_all_notes()

    # Construct the note dictionary
    new_note = {
        "id": generate_new_id(notes),
        "subject": subject,
        "title": title,
        "content": content,
        "author": current_user
    }

    # Append new note and save
    notes.append(new_note)
    save_data(NOTES_FILE, notes)
    print(f"\nNote added successfully! (ID: {new_note['id']})")


def view_all_notes():
    """
    Displays all notes currently stored in the system.
    """
    print("\n--- All Shared Notes ---")
    notes = get_all_notes()

    # Check if there are no notes
    if not notes:
        print("No notes available.")
        return

    # Iterate and display each note
    for note in notes:
        print(f"\nID: {note['id']}")
        print(f"Subject: {note['subject']}")
        print(f"Title: {note['title']}")
        print(f"Author: {note['author']}")
        print(f"Content: {note['content']}")
        print("-" * 30)


def search_notes_by_subject():
    """
    Prompts for a subject keyword and displays all matching notes.
    Search is case-insensitive.
    """
    print("\n--- Search Notes by Subject ---")
    query = input("Enter subject name to search: ").strip().lower()

    if not query:
        print("Search query cannot be empty.")
        return

    notes = get_all_notes()
    matches = []

    # Loop through notes and match subject
    for note in notes:
        if query in note.get("subject", "").lower():
            matches.append(note)

    # Check if any matches were found
    if not matches:
        print(f"No notes found matching subject: '{query}'")
        return

    print(f"\nFound {len(matches)} note(s):")
    for note in matches:
        print(f"\nID: {note['id']}")
        print(f"Subject: {note['subject']}")
        print(f"Title: {note['title']}")
        print(f"Author: {note['author']}")
        print(f"Content: {note['content']}")
        print("-" * 30)


def delete_my_note(current_user):
    """
    Allows the logged-in user to delete only notes authored by them.
    """
    print("\n--- Delete My Note ---")
    notes = get_all_notes()

    # Filter notes that belong to the current user
    user_notes = []
    for note in notes:
        if note.get("author") == current_user:
            user_notes.append(note)

    # Check if user has authored any notes
    if not user_notes:
        print("You haven't authored any notes yet.")
        return

    # Display user's own notes for reference
    print("Your notes:")
    for note in user_notes:
        print(f"[{note['id']}] {note['subject']}: {note['title']}")

    note_id_input = input("\nEnter the ID of the note to delete: ").strip()

    # Validate numeric input
    if not note_id_input.isdigit():
        print("Invalid ID. Please enter a valid number.")
        return

    target_id = int(note_id_input)

    # Search and remove the note if it exists and belongs to current_user
    found = False
    updated_notes = []
    for note in notes:
        if note["id"] == target_id:
            if note["author"] == current_user:
                found = True
                # Skip appending this note to delete it
                continue
            else:
                print("Permission denied: You can only delete your own notes.")
                return
        updated_notes.append(note)

    if found:
        save_data(NOTES_FILE, updated_notes)
        print(f"Note {target_id} deleted successfully.")
    else:
        print(f"No note found with ID {target_id} under your account.")


def notes_menu(current_user):
    """
    Main loop displaying the notes menu and handling user choices.
    """
    while True:
        print("\n===============================")
        print(f"  StudySphere - Notes Menu")
        print(f"  Logged in as: {current_user}")
        print("===============================")
        print("1. Add note")
        print("2. View all notes")
        print("3. Search notes by subject")
        print("4. Delete my note")
        print("5. Back")

        choice = input("Enter choice (1-5): ").strip()

        if choice == "1":
            add_note(current_user)
        elif choice == "2":
            view_all_notes()
        elif choice == "3":
            search_notes_by_subject()
        elif choice == "4":
            delete_my_note(current_user)
        elif choice == "5":
            print("Returning to main menu...")
            break
        else:
            print("Invalid selection. Please choose between 1 and 5.")