#Import necessary libraries
import os

def move_files(path):
    '''This function will eventually contain the logic to move files based on configuration rules.'''
    print(f"Scanning directory: {path}")

    #1. Get everything inside the folder
    items = os.listdir(path)

    #2. Print the list of items (files and folders)
    print("Items found in the directory:")
    for item in items:
        full_path = os.path.join(path, item)
        if os.path.isdir(full_path):
            print(f"- directory: {item}")
        elif os.path.isfile(full_path):
            print(f"- file: {item}")

    print(f"[PHASE 1] move_files called with path: {path}")
    print("[PHASE 1] Not implemented yet.")
