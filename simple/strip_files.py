import os
import re

def strip_files():
    folder_path = input("Enter the folder path: ").strip()
    pattern = input("Enter the regex pattern to remove: ").strip()

    for filename in os.listdir(folder_path):
        new_name = re.sub(pattern, '', filename).strip()
        if new_name != filename:  # Rename only if a change is made
            os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, new_name))
            print(f'Renamed: {filename} -> {new_name}')

# Example usage
strip_files()
