"""Registration, login, and profile tools for StudySphere.

Expected storage.py interface:
    load_data(filename, default_data) -> Python object
    save_data(filename, data) -> None

User data is stored in users.json as a dictionary keyed by username.
"""

import hashlib

from storage import load_data, save_data


USERS_FILE = "users.json"


def _read_users():
    """Load user records, using an empty dictionary for a new project."""
    users = load_data(USERS_FILE, {})
    # Keep the module safe if the JSON file is empty or has the wrong shape.
    return users if isinstance(users, dict) else {}


def _save_users(users):
    """Save all user records through the shared storage module."""
    save_data(USERS_FILE, users)


def _password_hash(password):
    """Return a consistent fingerprint of a password for JSON storage."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def register():
    """Register a new account. Returns its username, or None if cancelled."""
    users = _read_users()
    print("\n--- Register ---")

    while True:
        username = input("Choose a username: ").strip()
        if not username:
            print("Username cannot be empty. Please try again.")
        elif username in users:
            print("That username is already taken. Please choose another.")
        else:
            break

    while True:
        password = input("Choose a password: ")
        if not password.strip():
            print("Password cannot be empty. Please try again.")
        else:
            break

    # Keep optional profile information ready for profile_menu().
    users[username] = {
        "password_hash": _password_hash(password),
        "name": "",
        "branch": "",
        "subjects": [],
    }
    _save_users(users)
    print("Registration successful. You can now log in.")
    return username


def login():
    """Check credentials and return the username on success, otherwise None."""
    users = _read_users()
    print("\n--- Login ---")
    username = input("Username: ").strip()
    password = input("Password: ")

    user = users.get(username)
    if user is None or user.get("password_hash") != _password_hash(password):
        print("Incorrect username or password.")
        return None

    print("Login successful. Welcome, {}!".format(username))
    return username


def profile_menu(current_user):
    """Show and edit the logged-in user's name, branch, and subjects."""
    if not current_user:
        print("Please log in to view your profile.")
        return

    users = _read_users()
    if current_user not in users:
        print("User account was not found.")
        return

    # Older records may not yet have these profile fields.
    profile = users[current_user]
    profile.setdefault("name", "")
    profile.setdefault("branch", "")
    profile.setdefault("subjects", [])

    while True:
        print("\n--- Profile ---")
        print("Username: {}".format(current_user))
        print("Name: {}".format(profile["name"] or "Not set"))
        print("Branch: {}".format(profile["branch"] or "Not set"))
        subjects = profile["subjects"]
        print("Subjects: {}".format(", ".join(subjects) if subjects else "Not set"))
        print("\n1. Edit name")
        print("2. Edit branch")
        print("3. Edit subjects")
        print("4. Return to main menu")

        choice = input("Choose an option: ").strip()
        if choice == "1":
            profile["name"] = input("Enter your name: ").strip()
            _save_users(users)
            print("Name updated.")
        elif choice == "2":
            profile["branch"] = input("Enter your branch: ").strip()
            _save_users(users)
            print("Branch updated.")
        elif choice == "3":
            entered_subjects = input(
                "Enter subjects separated by commas (example: Maths, Physics): "
            )
            # Remove extra spaces and ignore empty entries.
            profile["subjects"] = [
                subject.strip()
                for subject in entered_subjects.split(",")
                if subject.strip()
            ]
            _save_users(users)
            print("Subjects updated.")
        elif choice == "4":
            return
        else:
            print("Please enter a number from 1 to 4.")
