import os
import glob

def prepend_numbers_to_audio_files(folder_path):
    # Get all audio files in the folder
    audio_files = glob.glob(os.path.join(folder_path, '*.mp3')) + \
                  glob.glob(os.path.join(folder_path, '*.wav')) + \
                  glob.glob(os.path.join(folder_path, '*.flac')) + \
                  glob.glob(os.path.join(folder_path, '*.aac')) + \
                  glob.glob(os.path.join(folder_path, '*.ogg')) + \
                  glob.glob(os.path.join(folder_path, '*.m4a'))

    # Sort files by creation time
    audio_files.sort(key=os.path.getctime)

    # Prepend numbers to file names
    for index, file_path in enumerate(audio_files, start=1):
        folder, file_name = os.path.split(file_path)
        new_file_name = f"{index:02d} - {file_name}"
        new_file_path = os.path.join(folder, new_file_name)
        os.rename(file_path, new_file_path)
        print(f"Renamed '{file_name}' to '{new_file_name}'")

if __name__ == "__main__":
    folder_path = input("Enter the folder path: ")
    prepend_numbers_to_audio_files(folder_path)
