import os
import glob
import re

def prepend_numbers_to_audio_files(folder_path, start_number):
    # Get all audio files in the folder
    audio_files = glob.glob(os.path.join(folder_path, '*.mp3')) + \
                  glob.glob(os.path.join(folder_path, '*.wav')) + \
                  glob.glob(os.path.join(folder_path, '*.flac')) + \
                  glob.glob(os.path.join(folder_path, '*.aac')) + \
                  glob.glob(os.path.join(folder_path, '*.ogg')) + \
                  glob.glob(os.path.join(folder_path, '*.m4a'))

    # Sort files by creation time
    audio_files.sort(key=os.path.getctime)

    # Prepend numbers to file names, ignoring files already numbered
    number_pattern = re.compile(r'^\d{3} - ')
    for index, file_path in enumerate(audio_files, start=start_number):
        folder, file_name = os.path.split(file_path)
        if number_pattern.match(file_name):
            print(f"Skipping already numbered file: {file_name}")
            continue
        new_file_name = f"{index:03d} - {file_name}"
        new_file_path = os.path.join(folder, new_file_name)
        os.rename(file_path, new_file_path)
        print(f"Renamed '{file_name}' to '{new_file_name}'")

    input("Renaming complete. Press Enter to exit.")

if __name__ == "__main__":
    folder_path = input("Enter the folder path: ")

    # Validate the start number
    while True:
        try:
            start_number = int(input("Enter the starting number (e.g., 001, 002, ...): "))
            if start_number < 0:
                print("Please enter a positive number.")
            else:
                break
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    prepend_numbers_to_audio_files(folder_path, start_number)
