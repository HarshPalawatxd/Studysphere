# storage.py
# Saves and loads data for all StudySphere features.

import json
import os


def load_data(filename, default_data=None):
    """Read a JSON file. If missing, empty or broken, return default_data (default: [])."""
    if default_data is None:
        default_data = []

    if not os.path.exists(filename):
        return default_data

    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return default_data


def save_data(filename, data):
    """Write data (list or dictionary) into a JSON file."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


# ---------- Test code ----------
if __name__ == "__main__":
    test_list = [{"name": "Shubh", "subject": "Python"}]
    save_data("test.json", test_list)
    loaded = load_data("test.json")
    print("Saved:", test_list)
    print("Loaded:", loaded)
    if loaded == test_list:
        print("storage.py is working correctly!")
    else:
        print("Something went wrong.")