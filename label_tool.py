import os
import pandas as pd
from pydub import AudioSegment
from pydub.playback import play

labels = []
for file in os.listdir("data"):
    if file.endswith(".wav"):
        audio = AudioSegment.from_file(f"data/{file}")
        play(audio)
        label = input(f"Enter label for {file} (0=normal, 1=hungry, 2=angry): ")
        labels.append({"file": file, "label": label})

df = pd.DataFrame(labels)
df.to_csv("data/labels.csv", index=False)