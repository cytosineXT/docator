import os
from pydub import AudioSegment
from pydub.playback import play

data_dir = 'data/all'

for file in os.listdir(data_dir):
    if file.endswith(".wav") and "_label" not in file:
        file_path = os.path.join(data_dir, file)
        
        # 播放音频
        audio = AudioSegment.from_file(file_path)
        play(audio)
        
        # 获取用户输入（新增删除标签3）
        label = input(f"Enter label for {file} (1=cat, 0=no, 2=cat+noise, 3=delete): ")
        
        if label == '3':
            # 删除文件
            os.remove(file_path)
            print(f"Deleted: {file}")
        elif label in ('0', '1', '2'):
            # 重命名文件
            new_file_name = f"{os.path.splitext(file)[0]}_label{label}.wav"
            new_file_path = os.path.join(data_dir, new_file_name)
            os.rename(file_path, new_file_path)
            print(f"Renamed: {file} -> {new_file_name}")
        else:
            print(f"Invalid label {label}, skipped {file}")
            
    else:
        print(f"Skipping {file}, already labeled.")

print('All items done.')