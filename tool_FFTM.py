import os
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
from scipy.fftpack import fft

# 设置目录
wav_dir = r"data/all"
save_dir = r"data_fft"
os.makedirs(save_dir, exist_ok=True)

# 遍历目录中的.wav文件
for file in os.listdir(wav_dir):
    if file.endswith(".wav"):
        image_path = os.path.join(save_dir, f"{os.path.splitext(file)[0]}.png")
        
        # 如果图像已存在，跳过
        if os.path.exists(image_path):
            print(f"Skipping {file}, analysis image already exists.")
            continue
        
        # 加载音频
        y, sr = librosa.load(os.path.join(wav_dir, file), sr=None)
        
        # 计算FFT
        fft_values = np.abs(fft(y))[:len(y)//2]
        freqs = np.linspace(0, sr/2, len(fft_values))
        
        # 计算梅尔频谱图
        mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=sr/2)
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        
        # 绘制FFT和梅尔频谱图在同一张图上
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        
        # 绘制FFT图，限制频率范围为0-15000Hz
        axes[0].plot(freqs, fft_values)
        axes[0].set_xlim([0, 15000])
        axes[0].set_xlabel("Frequency (Hz)")
        axes[0].set_ylabel("Amplitude")
        axes[0].set_title(f"FFT Spectrum of {file}")
        
        # 绘制梅尔频谱图
        img = librosa.display.specshow(mel_spec_db, sr=sr, x_axis='time', y_axis='mel', ax=axes[1])
        fig.colorbar(img, ax=axes[1], format='%+2.0f dB')
        axes[1].set_title(f"Mel Spectrogram of {file}")
        
        # 保存图片
        plt.tight_layout()
        plt.savefig(image_path)
        plt.close()
        
        print(f"Processed {file} and saved analysis image as {image_path}.")