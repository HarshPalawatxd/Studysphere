# gui.py - Tkinter app version of StudySphere
# Same data files (users.json, notes.json, ...) and same storage.py as the console version.
# Run:  python gui.py   (keep it in the same folder as storage.py)

import os
import hashlib
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

from storage import load_data, save_data

os.chdir(os.path.dirname(os.path.abspath(__file__)))

USERS_FILE = "users.json"
NOTES_FILE = "notes.json"
DOUBTS_FILE = "doubts.json"
CHAT_FILE = "chat.json"
EXAMS_FILE = "exams.json"
TODO_FILE = "todo.json"
DATE_FORMAT = "%d-%m-%Y"
SHOW_LAST = 20


# ---------------- helpers ----------------
def read_list(filename):
    data = load_data(filename)
    return data if isinstance(data, list) else []


def read_users():
    users = load_data(USERS_FILE, {})
    return users if isinstance(users, dict) else {}


def pw_hash(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def next_id(items):
    return max([i.get("id", 0) for i in items], default=0) + 1


def make_tree(parent, columns, widths, height=8):
    frame = ttk.Frame(parent)
    frame.pack(fill="both", expand=True, padx=8, pady=4)
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=height,
                        selectmode="browse")
    for col, w in zip(columns, widths):
        tree.heading(col, text=col.capitalize())
        tree.column(col, width=w, anchor="w")
    sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    return tree


def selected_id(tree):
    sel = tree.selection()
    return int(sel[0]) if sel else None


def make_text(parent, height=6):
    t = tk.Text(parent, height=height, wrap="word", state="disabled")
    t.pack(fill="x", padx=8, pady=4)
    return t


def set_text(widget, content):
    widget.config(state="normal")
    widget.delete("1.0", "end")
    widget.insert("1.0", content)
    widget.config(state="disabled")


def ask_fields(parent, title, fields):
    """fields = [(key, label, multiline)] -> dict of values, or None if cancelled."""
    win = tk.Toplevel(parent)
    win.title(title)
    win.transient(parent)
    win.grab_set()
    widgets = {}
    for i, (key, label, multi) in enumerate(fields):
        ttk.Label(win, text=label).grid(row=i, column=0, sticky="ne", padx=8, pady=6)
        w = tk.Text(win, width=40, height=6) if multi else ttk.Entry(win, width=42)
        w.grid(row=i, column=1, padx=8, pady=6)
        widgets[key] = w
    result = {}

    def get(w):
        return w.get("1.0", "end").strip() if isinstance(w, tk.Text) else w.get().strip()

    def ok():
        result.update({k: get(w) for k, w in widgets.items()})
        win.destroy()

    btns = ttk.Frame(win)
    btns.grid(row=len(fields), column=0, columnspan=2, pady=8)
    ttk.Button(btns, text="OK", command=ok).pack(side="left", padx=5)
    ttk.Button(btns, text="Cancel", command=win.destroy).pack(side="left", padx=5)
    list(widgets.values())[0].focus_set()
    parent.wait_window(win)
    return result or None


# ---------------- tabs ----------------
class NotesTab(ttk.Frame):
    def __init__(self, master, user):
        super().__init__(master)
        self.user = user
        self.notes = {}

        top = ttk.Frame(self)
        top.pack(fill="x", padx=8, pady=6)
        self.q = tk.StringVar()
        ttk.Label(top, text="Search subject:").pack(side="left")
        e = ttk.Entry(top, textvariable=self.q)
        e.pack(side="left", padx=5)
        e.bind("<Return>", lambda _: self.refresh())
        ttk.Button(top, text="Search", command=self.refresh).pack(side="left")
        ttk.Button(top, text="Show all", command=self.show_all).pack(side="left", padx=4)

        self.tree = make_tree(self, ("id", "subject", "title", "author"), (50, 130, 250, 110))
        self.tree.bind("<<TreeviewSelect>>", self.show_detail)
        self.detail = make_text(self)

        bar = ttk.Frame(self)
        bar.pack(pady=6)
        ttk.Button(bar, text="Add Note", command=self.add).pack(side="left", padx=5)
        ttk.Button(bar, text="Delete My Note", command=self.delete).pack(side="left", padx=5)

    def show_all(self):
        self.q.set("")
        self.refresh()

    def refresh(self):
        query = self.q.get().strip().lower()
        self.tree.delete(*self.tree.get_children())
        self.notes = {}
        for n in read_list(NOTES_FILE):
            if query and query not in n.get("subject", "").lower():
                continue
            self.notes[n["id"]] = n
            self.tree.insert("", "end", iid=str(n["id"]),
                             values=(n["id"], n["subject"], n["title"], n["author"]))
        set_text(self.detail, "")

    def show_detail(self, _=None):
        nid = selected_id(self.tree)
        if nid in self.notes:
            set_text(self.detail, self.notes[nid]["content"])

    def add(self):
        r = ask_fields(self, "Add Note", [("subject", "Subject", False),
                                          ("title", "Title", False),
                                          ("content", "Content", True)])
        if not r:
            return
        if not all(r.values()):
            messagebox.showerror("Error", "All fields are required.")
            return
        notes = read_list(NOTES_FILE)
        notes.append({"id": next_id(notes), "subject": r["subject"], "title": r["title"],
                      "content": r["content"], "author": self.user})
        save_data(NOTES_FILE, notes)
        self.refresh()

    def delete(self):
        nid = selected_id(self.tree)
        if nid is None:
            messagebox.showinfo("Delete", "Pehle list me se ek note select karo.")
            return
        notes = read_list(NOTES_FILE)
        target = next((n for n in notes if n["id"] == nid), None)
        if not target or target["author"] != self.user:
            messagebox.showerror("Permission denied", "You can only delete your own notes.")
            return
        if messagebox.askyesno("Delete", "Ye note delete karna hai?"):
            save_data(NOTES_FILE, [n for n in notes if n["id"] != nid])
            self.refresh()


class DoubtsTab(ttk.Frame):
    def __init__(self, master, user):
        super().__init__(master)
        self.user = user
        self.doubts = {}
        self.tree = make_tree(self, ("id", "status", "subject", "question", "author"),
                              (50, 80, 120, 330, 100))
        self.tree.bind("<<TreeviewSelect>>", self.show_detail)
        self.detail = make_text(self, 7)
        bar = ttk.Frame(self)
        bar.pack(pady=6)
        ttk.Button(bar, text="Post Doubt", command=self.post).pack(side="left", padx=5)
        ttk.Button(bar, text="Answer", command=self.answer).pack(side="left", padx=5)
        ttk.Button(bar, text="Mark My Doubt Resolved", command=self.resolve).pack(side="left", padx=5)

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        self.doubts = {}
        for d in read_list(DOUBTS_FILE):
            self.doubts[d["id"]] = d
            status = "Resolved" if d.get("resolved") else "Open"
            self.tree.insert("", "end", iid=str(d["id"]),
                             values=(d["id"], status, d["subject"], d["question"], d["author"]))
        set_text(self.detail, "")

    def show_detail(self, _=None):
        d = self.doubts.get(selected_id(self.tree))
        if not d:
            return
        lines = ["Question: " + d["question"], ""]
        answers = d.get("answers", [])
        if answers:
            lines.append("Answers:")
            lines += ["  - {}: {}".format(a["author"], a["text"]) for a in answers]
        else:
            lines.append("Answers: none yet")
        set_text(self.detail, "\n".join(lines))

    def post(self):
        r = ask_fields(self, "Post a Doubt", [("subject", "Subject", False),
                                              ("question", "Your doubt", True)])
        if not r:
            return
        if not all(r.values()):
            messagebox.showerror("Error", "All fields are required.")
            return
        doubts = read_list(DOUBTS_FILE)
        doubts.append({"id": next_id(doubts), "subject": r["subject"], "question": r["question"],
                       "author": self.user, "answers": [], "resolved": False})
        save_data(DOUBTS_FILE, doubts)
        self.refresh()

    def answer(self):
        did = selected_id(self.tree)
        if did is None:
            messagebox.showinfo("Answer", "Pehle ek doubt select karo.")
            return
        text = simpledialog.askstring("Answer", "Your answer:", parent=self)
        if not text or not text.strip():
            return
        doubts = read_list(DOUBTS_FILE)
        for d in doubts:
            if d["id"] == did:
                d.setdefault("answers", []).append({"author": self.user, "text": text.strip()})
        save_data(DOUBTS_FILE, doubts)
        self.refresh()
        self.tree.selection_set(str(did))

    def resolve(self):
        did = selected_id(self.tree)
        if did is None:
            messagebox.showinfo("Resolve", "Pehle ek doubt select karo.")
            return
        doubts = read_list(DOUBTS_FILE)
        for d in doubts:
            if d["id"] == did:
                if d["author"] != self.user:
                    messagebox.showerror("Permission denied",
                                         "Only the author can resolve a doubt.")
                    return
                d["resolved"] = True
        save_data(DOUBTS_FILE, doubts)
        self.refresh()


class ChatTab(ttk.Frame):
    def __init__(self, master, user):
        super().__init__(master)
        self.user = user
        self.box = tk.Text(self, state="disabled", wrap="word")
        self.box.pack(fill="both", expand=True, padx=8, pady=8)
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=8, pady=6)
        self.msg = tk.StringVar()
        e = ttk.Entry(bar, textvariable=self.msg)
        e.pack(side="left", fill="x", expand=True)
        e.bind("<Return>", lambda _: self.send())
        ttk.Button(bar, text="Send", command=self.send).pack(side="left", padx=5)
        ttk.Button(bar, text="Refresh", command=self.refresh).pack(side="left")
        self._tick()

    def _tick(self):
        if self.winfo_exists():
            self.refresh()
            self.after(4000, self._tick)

    def refresh(self):
        msgs = read_list(CHAT_FILE)[-SHOW_LAST:]
        text = "\n".join("[{}] {}: {}".format(m["time"], m["user"], m["text"]) for m in msgs)
        set_text(self.box, text or "No messages yet. Start the conversation!")
        self.box.see("end")

    def send(self):
        text = self.msg.get().strip()
        if not text:
            return
        msgs = read_list(CHAT_FILE)
        msgs.append({"user": self.user, "text": text,
                     "time": datetime.now().strftime("%d-%m-%Y %H:%M")})
        save_data(CHAT_FILE, msgs)
        self.msg.set("")
        self.refresh()


class ExamsTab(ttk.Frame):
    def __init__(self, master, user):
        super().__init__(master)
        self.user = user
        self.tree = make_tree(self, ("id", "subject", "date", "status"), (50, 220, 120, 160), 12)
        bar = ttk.Frame(self)
        bar.pack(pady=6)
        ttk.Button(bar, text="Add Exam", command=self.add).pack(side="left", padx=5)
        ttk.Button(bar, text="Delete Exam", command=self.delete).pack(side="left", padx=5)

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        mine = [e for e in read_list(EXAMS_FILE) if e.get("user") == self.user]
        mine.sort(key=lambda e: datetime.strptime(e["date"], DATE_FORMAT))
        today = datetime.now().date()
        for e in mine:
            left = (datetime.strptime(e["date"], DATE_FORMAT).date() - today).days
            note = "{} day(s) left".format(left) if left > 0 else ("Today!" if left == 0 else "Completed")
            self.tree.insert("", "end", iid=str(e["id"]),
                             values=(e["id"], e["subject"], e["date"], note))

    def add(self):
        r = ask_fields(self, "Add Exam", [("subject", "Subject", False),
                                          ("date", "Date (DD-MM-YYYY)", False)])
        if not r:
            return
        try:
            datetime.strptime(r["date"], DATE_FORMAT)
            if not r["subject"]:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Subject daalo aur date DD-MM-YYYY me (e.g. 25-12-2026).")
            return
        exams = read_list(EXAMS_FILE)
        exams.append({"id": next_id(exams), "subject": r["subject"], "date": r["date"],
                      "user": self.user})
        save_data(EXAMS_FILE, exams)
        self.refresh()

    def delete(self):
        eid = selected_id(self.tree)
        if eid is None:
            messagebox.showinfo("Delete", "Pehle ek exam select karo.")
            return
        save_data(EXAMS_FILE, [e for e in read_list(EXAMS_FILE) if e["id"] != eid])
        self.refresh()


class TodoTab(ttk.Frame):
    def __init__(self, master, user):
        super().__init__(master)
        self.user = user
        top = ttk.Frame(self)
        top.pack(fill="x", padx=8, pady=6)
        self.new = tk.StringVar()
        e = ttk.Entry(top, textvariable=self.new)
        e.pack(side="left", fill="x", expand=True)
        e.bind("<Return>", lambda _: self.add())
        ttk.Button(top, text="Add Task", command=self.add).pack(side="left", padx=5)
        self.tree = make_tree(self, ("done", "id", "task"), (60, 50, 480), 12)
        bar = ttk.Frame(self)
        bar.pack(pady=6)
        ttk.Button(bar, text="Mark Done", command=self.mark_done).pack(side="left", padx=5)
        ttk.Button(bar, text="Delete Task", command=self.delete).pack(side="left", padx=5)

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for t in read_list(TODO_FILE):
            if t.get("user") == self.user:
                self.tree.insert("", "end", iid=str(t["id"]),
                                 values=("[x]" if t["done"] else "[ ]", t["id"], t["title"]))

    def add(self):
        title = self.new.get().strip()
        if not title:
            return
        tasks = read_list(TODO_FILE)
        tasks.append({"id": next_id(tasks), "title": title, "done": False, "user": self.user})
        save_data(TODO_FILE, tasks)
        self.new.set("")
        self.refresh()

    def mark_done(self):
        tid = selected_id(self.tree)
        if tid is None:
            return
        tasks = read_list(TODO_FILE)
        for t in tasks:
            if t["id"] == tid and t["user"] == self.user:
                t["done"] = True
        save_data(TODO_FILE, tasks)
        self.refresh()

    def delete(self):
        tid = selected_id(self.tree)
        if tid is None:
            return
        tasks = read_list(TODO_FILE)
        save_data(TODO_FILE, [t for t in tasks if not (t["id"] == tid and t["user"] == self.user)])
        self.refresh()


class ProfileTab(ttk.Frame):
    def __init__(self, master, user):
        super().__init__(master)
        self.user = user
        form = ttk.Frame(self)
        form.pack(pady=30)
        self.vars = {k: tk.StringVar() for k in ("name", "branch", "subjects")}
        ttk.Label(form, text="Username:").grid(row=0, column=0, sticky="e", padx=8, pady=8)
        ttk.Label(form, text=user, font=("Arial", 11, "bold")).grid(row=0, column=1, sticky="w")
        rows = [("Name:", "name"), ("Branch:", "branch"), ("Subjects (comma separated):", "subjects")]
        for i, (label, key) in enumerate(rows, start=1):
            ttk.Label(form, text=label).grid(row=i, column=0, sticky="e", padx=8, pady=8)
            ttk.Entry(form, textvariable=self.vars[key], width=40).grid(row=i, column=1, pady=8)
        ttk.Button(form, text="Save Profile", command=self.save).grid(row=4, column=1, sticky="w", pady=12)

    def refresh(self):
        p = read_users().get(self.user, {})
        self.vars["name"].set(p.get("name", ""))
        self.vars["branch"].set(p.get("branch", ""))
        self.vars["subjects"].set(", ".join(p.get("subjects", [])))

    def save(self):
        users = read_users()
        if self.user not in users:
            messagebox.showerror("Error", "User account was not found.")
            return
        users[self.user]["name"] = self.vars["name"].get().strip()
        users[self.user]["branch"] = self.vars["branch"].get().strip()
        users[self.user]["subjects"] = [s.strip() for s in self.vars["subjects"].get().split(",")
                                        if s.strip()]
        save_data(USERS_FILE, users)
        messagebox.showinfo("Profile", "Profile saved!")


# ---------------- app ----------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("StudySphere")
        self.geometry("920x620")
        self.minsize(800, 540)
        self.show_login()

    def clear(self):
        for w in self.winfo_children():
            w.destroy()

    # ----- login / register screen -----
    def show_login(self):
        self.clear()
        box = ttk.Frame(self)
        box.place(relx=0.5, rely=0.5, anchor="center")
        ttk.Label(box, text="StudySphere", font=("Arial", 30, "bold")).pack(pady=(0, 4))
        ttk.Label(box, text="Your study group platform", font=("Arial", 11)).pack(pady=(0, 20))

        self.u = tk.StringVar()
        self.p = tk.StringVar()
        ttk.Label(box, text="Username").pack(anchor="w")
        eu = ttk.Entry(box, textvariable=self.u, width=32)
        eu.pack(pady=(0, 10))
        ttk.Label(box, text="Password").pack(anchor="w")
        ep = ttk.Entry(box, textvariable=self.p, show="*", width=32)
        ep.pack(pady=(0, 16))
        ep.bind("<Return>", lambda _: self.login())

        row = ttk.Frame(box)
        row.pack()
        ttk.Button(row, text="Login", command=self.login, width=14).pack(side="left", padx=5)
        ttk.Button(row, text="Register", command=self.register, width=14).pack(side="left", padx=5)
        eu.focus_set()

    def login(self):
        username, password = self.u.get().strip(), self.p.get()
        user = read_users().get(username)
        if user is None or user.get("password_hash") != pw_hash(password):
            messagebox.showerror("Login failed", "Incorrect username or password.")
            return
        self.show_main(username)

    def register(self):
        username, password = self.u.get().strip(), self.p.get()
        users = read_users()
        if not username:
            messagebox.showerror("Register", "Username cannot be empty.")
        elif username in users:
            messagebox.showerror("Register", "That username is already taken.")
        elif not password.strip():
            messagebox.showerror("Register", "Password cannot be empty.")
        else:
            users[username] = {"password_hash": pw_hash(password), "name": "",
                               "branch": "", "subjects": []}
            save_data(USERS_FILE, users)
            messagebox.showinfo("Register", "Registration successful. Now login into Studysphere.")

    # ----- main screen -----
    def show_main(self, user):
        self.clear()
        header = ttk.Frame(self)
        header.pack(fill="x", padx=10, pady=8)
        ttk.Label(header, text="StudySphere", font=("Arial", 18, "bold")).pack(side="left")
        ttk.Button(header, text="Logout", command=self.show_login).pack(side="right")
        ttk.Label(header, text="Logged in as: " + user).pack(side="right", padx=12)

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        tabs = [("Notes", NotesTab), ("Doubt Board", DoubtsTab), ("Chat Room", ChatTab),
                ("Exam Tracker", ExamsTab), ("To-Do List", TodoTab), ("Profile", ProfileTab)]
        for name, cls in tabs:
            nb.add(cls(nb, user), text=name)

        def refresh_current(_=None):
            tab = nb.nametowidget(nb.select())
            tab.refresh()

        nb.bind("<<NotebookTabChanged>>", refresh_current)
        self.after(50, refresh_current)


if __name__ == "__main__":
    App().mainloop()