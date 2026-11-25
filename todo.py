 # todo.py - Personal to-do list for StudySphere

from storage import load_data, save_data

TODO_FILE = "todo.json"


def get_all_tasks():
    tasks = load_data(TODO_FILE)
    return tasks if isinstance(tasks, list) else []


def generate_new_id(tasks):
    max_id = 0
    for t in tasks:
        if t.get("id", 0) > max_id:
            max_id = t["id"]
    return max_id + 1


def get_user_tasks(tasks, current_user):
    return [t for t in tasks if t.get("user") == current_user]


def add_task(current_user):
    title = input("Task: ").strip()
    if not title:
        print("Task cannot be empty.")
        return

    tasks = get_all_tasks()
    new_task = {
        "id": generate_new_id(tasks),
        "title": title,
        "done": False,
        "user": current_user,
    }
    tasks.append(new_task)
    save_data(TODO_FILE, tasks)
    print(f"Task added! (ID: {new_task['id']})")


def view_tasks(current_user):
    print("\n--- My Tasks ---")
    my_tasks = get_user_tasks(get_all_tasks(), current_user)
    if not my_tasks:
        print("No tasks yet.")
        return
    for t in my_tasks:
        mark = "[x]" if t["done"] else "[ ]"
        print(f"{mark} {t['id']}. {t['title']}")


def mark_done(current_user):
    tasks = get_all_tasks()
    my_tasks = get_user_tasks(tasks, current_user)
    if not my_tasks:
        print("No tasks to update.")
        return

    task_id = input("Enter task ID to mark done: ").strip()
    if not task_id.isdigit():
        print("Invalid ID.")
        return

    for t in tasks:
        if t["id"] == int(task_id) and t["user"] == current_user:
            t["done"] = True
            save_data(TODO_FILE, tasks)
            print("Task marked as done.")
            return
    print("No task found with that ID under your account.")


def delete_task(current_user):
    tasks = get_all_tasks()
    my_tasks = get_user_tasks(tasks, current_user)
    if not my_tasks:
        print("No tasks to delete.")
        return

    task_id = input("Enter task ID to delete: ").strip()
    if not task_id.isdigit():
        print("Invalid ID.")
        return

    target = int(task_id)
    if not any(t["id"] == target for t in my_tasks):
        print("No task found with that ID under your account.")
        return

    save_data(TODO_FILE, [t for t in tasks if t["id"] != target])
    print("Task deleted.")


def todo_menu(current_user):
    while True:
        print("\n===============================")
        print("  StudySphere - To-Do List")
        print(f"  Logged in as: {current_user}")
        print("===============================")
        print("1. Add task")
        print("2. View my tasks")
        print("3. Mark task done")
        print("4. Delete task")
        print("5. Back")

        choice = input("Enter choice (1-5): ").strip()

        if choice == "1":
            add_task(current_user)
        elif choice == "2":
            view_tasks(current_user)
        elif choice == "3":
            mark_done(current_user)
        elif choice == "4":
            delete_task(current_user)
        elif choice == "5":
            print("Returning to main menu...")
            break
        else:
            print("Invalid selection. Please choose between 1 and 5.")