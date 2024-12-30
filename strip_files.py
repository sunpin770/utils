
import os

def strip_files():
    folder_path = input("Enter the folder path: ")
    common_string = input("Enter the common string to remove: ")
    for filename in os.listdir(folder_path):
        if filename.startswith(common_string):
            new_name = filename[len(common_string):].strip()
            os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, new_name))

# Example usage
strip_files()
