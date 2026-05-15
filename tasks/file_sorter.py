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
        print(f"- {item}")
    print(f"[PHASE 1] move_files called with path: {path}")
    print("[PHASE 1] Not implemented yet.")
