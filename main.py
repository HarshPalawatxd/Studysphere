 #"""Main program for StudySphere, the console-based study group platform."""

import notes
import doubts
import chat
import exams
import todo
import users


def get_current_user():
    """Keep showing the welcome options until a user logs in or registers."""
    print("=" * 40)
    print("Welcome to StudySphere")
    print("=" * 40)

    while True:
        print("\n1. Login")
        print("2. Register")
        print("3. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            current_user = users.login()
            if current_user:
                return current_user
        elif choice == "2":
            # Registration only creates the account; the user then logs in.
            users.register()
        elif choice == "3":
            print("Goodbye! Thanks for using StudySphere.")
            return None
        else:
            print("Please enter 1, 2, or 3.")


def main_menu(current_user):
    """Display the feature menu and open the selected feature."""
    while True:
        print("\n--- Main Menu ---")
        print("1. Notes")
        print("2. Doubt Board")
        print("3. Chat Room")
        print("4. Exam Tracker")
        print("5. To-Do List")
        print("6. Profile")
        print("7. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            notes.notes_menu(current_user)
        elif choice == "2":
            doubts.doubts_menu(current_user)
        elif choice == "3":
            chat.chat_menu(current_user)
        elif choice == "4":
            exams.exams_menu(current_user)
        elif choice == "5":
            todo.todo_menu(current_user)
        elif choice == "6":
            users.profile_menu(current_user)
        elif choice == "7":
            print("Goodbye, {}!".format(current_user))
            break
        else:
            print("Please enter a number from 1 to 7.")


def run_studysphere():
    """Start StudySphere after account authentication."""
    current_user = get_current_user()
    if current_user:
        main_menu(current_user)


# Run the program only when this file is started directly.
if __name__ == "__main__":
    run_studysphere()