import pyaudio
import wave
import time
import numpy as np
import os
import librosa

# 配置参数
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
THRESHOLD = 100  # 音量阈值，需根据环境调整
SILENT_CHUNKS = 0.1 * RATE / CHUNK  # 持续0.1秒
VOLUME_HISTORY_LENGTH = 10  # 音量显示平滑系数
from datetime import datetime
date = datetime.today().strftime("%m%d")
savedir = f"data/data{date}"

# def calculate_duration(buffer, chunk, rate):
#     return len(buffer) * chunk / rate

# def calculate_peak(buffer):
#     audio_data = np.concatenate(buffer)
#     return np.max(np.abs(audio_data)) if len(audio_data) > 0 else 0

def save_audio(data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(data))

def check_audio(file_path):
    """检查音频文件是否符合要求"""
    try:
        y, sr = librosa.load(file_path, sr=None, mono=True)
        duration = librosa.get_duration(y=y, sr=sr)
        peak = np.max(np.abs(y))
        return duration, peak
    except Exception as e:
        print(f"无法读取文件 {file_path}: {e}")
        return None, None

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
            print(f"\n检测到猫叫！开始录音... [{time.strftime('%H:%M:%S')}]")
            audio_buffer = [data]
            silent_count = 0
        elif is_recording:
            audio_buffer.append(data)
            if smoothed_volume < THRESHOLD:
                silent_count += 1
                if silent_count > SILENT_CHUNKS:
                    is_recording = False
                    # 在内存中处理音频数据
                    audio_bytes = b''.join(audio_buffer)
                    audio_np = np.frombuffer(audio_bytes, dtype=np.int16)
                    duration = len(audio_np) / RATE  # 计算时长
                    peak = np.max(np.abs(audio_np)) / 32768.0

                    # 有效性检查
                    valid = True
                    reason = []
                    if duration < 0.6:
                        valid = False
                        reason.append("时长不足")
                    elif duration > 4:
                        valid = False
                        reason.append("时长过长")
                    if peak < 0.04:
                        valid = False
                        reason.append("音量过小")
                    elif peak > 0.5:  # 修正了原代码中的0.5阈值错误
                        valid = False
                        reason.append("音量过大")

                    if valid:
                        filename = os.path.join(savedir, time.strftime("%Y%m%d_%H%M%S") + ".wav")
                        save_audio(audio_buffer, filename)
                        print(f"\n🔥 有效录音已保存：{filename} [时长:{duration:.2f}s 峰值:{peak:.3f}]")
                    else:
                        print(f"\n⏩ 无效录音已丢弃：{'+'.join(reason)} [时长:{duration:.2f}s 峰值:{peak:.3f}]")
            else:
                silent_count = 0
except KeyboardInterrupt:
    print("\n\n🛑 程序已停止")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()