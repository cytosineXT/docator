import os
import numpy as np
import librosa

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

def process_directory(directory):
    """处理目录中的音频文件"""
    deleted_files = 0
    total_files = 0
    
    for filename in os.listdir(directory):
        if not filename.endswith('.wav'):
            continue
            
        total_files += 1
        file_path = os.path.join(directory, filename)
        
        # 检查音频参数
        duration, peak = check_audio(file_path)
        if duration is None or peak is None:
            continue
            
        # 判断删除条件
        delete_reason = []
        if duration < 0.6:
            delete_reason.append(f"时长不足({duration:.2f}s)")
        if duration >4:
            delete_reason.append(f"时长过长({duration:.2f}s)")
        if peak < 0.04:
            delete_reason.append(f"峰值过低({peak:.4f})")
        if peak > 0.25:
            delete_reason.append(f"峰值过高({peak:.4f})")
            
        if delete_reason:
            try:
                os.remove(file_path)
                deleted_files += 1
                print(f"已删除 {filename}: {', '.join(delete_reason)}")
            except Exception as e:
                print(f"删除失败 {filename}: {str(e)}")
    
    # 打印统计结果
    print(f"\n处理完成：")
    print(f"总文件数：{total_files}")
    print(f"已删除文件：{deleted_files}")
    print(f"剩余文件：{total_files - deleted_files}")

if __name__ == "__main__":
    target_dir = r"data/all"  # 修改为实际目录路径
    
    # 安全确认
    confirm = input(f"即将处理目录：{target_dir}\n确认执行删除操作？(y/n) ")
    if confirm.lower() == 'y':
        process_directory(target_dir)
    else:
        print("操作已取消")