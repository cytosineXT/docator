import os
from pydub import AudioSegment
from pydub.playback import play

data_dir = 'data'

for file in os.listdir(data_dir):
    if file.endswith(".wav") and "_label" not in file:
        file_path = os.path.join(data_dir, file)
        audio = AudioSegment.from_file(file_path)
        play(audio)
        label = input(f"Enter label for {file} (1=cat, 0=no, 2=cat+noise): ")
        
        new_file_name = f"{os.path.splitext(file)[0]}_label{label}.wav"
        new_file_path = os.path.join(data_dir, new_file_name)
        os.rename(file_path, new_file_path)
        print(f"Renamed: {file} -> {new_file_name}")
    else:
        print(f"Skipping {file}, already labeled.")

print('All items done.')