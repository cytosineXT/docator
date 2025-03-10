import pyaudio
import wave
import time
import numpy as np
import os

# 配置参数
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
THRESHOLD = 100  # 音量阈值，需根据环境调整
SILENT_CHUNKS = 0.1 * RATE / CHUNK  # 持续1秒
VOLUME_HISTORY_LENGTH = 10  # 音量显示平滑系数
from datetime import datetime
date = datetime.today().strftime("%m%d")
savedir = f"data/data{date}"

def save_audio(data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(data))

# 初始化音频流
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                input=True, frames_per_buffer=CHUNK)

# 状态变量
audio_buffer = []
is_recording = False
silent_count = 0
volume_history = []

# 创建数据目录
os.makedirs(savedir, exist_ok=True)

try:
    print("实时音量监测中...（按Ctrl+C停止）")
    while True:
        # 读取音频数据
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        
        # 计算平滑音量值
        current_volume = np.abs(audio_data).mean()
        volume_history.append(current_volume)
        if len(volume_history) > VOLUME_HISTORY_LENGTH:
            volume_history.pop(0)
        smoothed_volume = np.mean(volume_history)

        # 实时显示（动态刷新）
        status = "🚨 HIGH!" if smoothed_volume > THRESHOLD else "✅ Normal"
        progress_bar = '█' * int(smoothed_volume // (THRESHOLD/10))
        print(f"\rVol: {smoothed_volume:6.1f} {progress_bar.ljust(10)} {status}", end="", flush=True)

        # 录音逻辑
        if smoothed_volume > THRESHOLD and not is_recording:
            is_recording = True
            print(f"\n🔥 检测到猫叫！开始录音... [{time.strftime('%H:%M:%S')}]")
            audio_buffer = [data]
            silent_count = 0
        elif is_recording:
            audio_buffer.append(data)
            if smoothed_volume < THRESHOLD:
                silent_count += 1
                if silent_count > SILENT_CHUNKS:
                    is_recording = False
                    # 使用 savedir 变量来构建文件名
                    filename = os.path.join(savedir, time.strftime("%Y%m%d_%H%M%S") + ".wav")
                    save_audio(audio_buffer, filename)
                    print(f"\n🎉 录音已保存：{filename} [{time.strftime('%H:%M:%S')}]")
            else:
                silent_count = 0

except KeyboardInterrupt:
    print("\n\n🛑 程序已停止")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()