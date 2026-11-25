# chat.py - Simple shared chat room for StudySphere

from datetime import datetime
from storage import load_data, save_data

CHAT_FILE = "chat.json"
SHOW_LAST = 20


def get_messages():
    messages = load_data(CHAT_FILE)
    return messages if isinstance(messages, list) else []


def send_message(current_user):
    text = input("Message: ").strip()
    if not text:
        print("Message cannot be empty.")
        return

    messages = get_messages()
    messages.append({
        "user": current_user,
        "text": text,
        "time": datetime.now().strftime("%d-%m-%Y %H:%M"),
    })
    save_data(CHAT_FILE, messages)
    print("Message sent!")


def view_messages():
    print(f"\n--- Last {SHOW_LAST} Messages ---")
    messages = get_messages()
    if not messages:
        print("No messages yet. Start the conversation!")
        return
    for m in messages[-SHOW_LAST:]:
        print(f"[{m['time']}] {m['user']}: {m['text']}")


def chat_menu(current_user):
    while True:
        print("\n===============================")
        print("  StudySphere - Chat Room")
        print(f"  Logged in as: {current_user}")
        print("===============================")
        print("1. Send message")
        print("2. View recent messages")
        print("3. Back")

        choice = input("Enter choice (1-3): ").strip()

        if choice == "1":
            send_message(current_user)
        elif choice == "2":
            view_messages()
        elif choice == "3":
            print("Returning to main menu...")
            break
        else:
            print("Invalid selection. Please choose between 1 and 3.")