import librosa
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from model import AudioClassifier
import panda as pd

class CatDataset(Dataset):
    def __init__(self, csv_file, audio_dir, sample_rate=16000, duration=1):
        self.df = pd.read_csv(csv_file)
        self.audio_dir = audio_dir
        self.sample_rate = sample_rate
        self.duration = duration

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        file = self.df.iloc[idx]['file']
        label = self.df.iloc[idx]['label']
        audio, _ = librosa.load(f"{self.audio_dir}/{file}", sr=self.sample_rate)
        
        # 统一音频长度
        if len(audio) > self.sample_rate * self.duration:
            audio = audio[:self.sample_rate * self.duration]
        else:
            audio = np.pad(audio, (0, max(0, self.sample_rate * self.duration - len(audio))))
        
        # 添加噪声增强
        noise = np.random.normal(0, 0.005, audio.shape)
        audio = audio + noise
        
        return torch.FloatTensor(audio).unsqueeze(0), torch.tensor(label)

# 训练代码
dataset = CatDataset("data/labels.csv", "data")
train_loader = DataLoader(dataset, batch_size=32, shuffle=True)

model = AudioClassifier()
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

for epoch in range(10):
    for inputs, labels in train_loader:
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    print(f"Epoch {epoch+1}, Loss: {loss.item():.4f}")

torch.save(model.state_dict(), "cat_classifier.pth")