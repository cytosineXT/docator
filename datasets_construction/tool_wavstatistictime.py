import os
import re
import numpy as np
import matplotlib.pyplot as plt
import librosa

def parse_label(filename):
    """从文件名中提取标签编号"""
    match = re.search(r'_label(\d)\.wav$', filename)
    return match.group(1) if match else None

base_dir = 'data/all'

# 初始化数据结构
labels = ['0', '1', '2']
durations = {label: [] for label in labels}

# 遍历目录处理文件
for filename in os.listdir(base_dir):
    if filename.endswith('.wav'):
        label = parse_label(filename)
        if label not in labels:
            continue
        
        file_path = os.path.join(base_dir, filename)
        try:
            y, sr = librosa.load(file_path, sr=None)
            duration = librosa.get_duration(y=y, sr=sr)
            durations[label].append(duration)
        except Exception as e:
            print(f"处理文件 {filename} 时出错: {e}")

# 创建可视化图表
plt.figure(figsize=(8, 9))

# 计算全局最大时长以统一坐标轴
all_durations = np.concatenate([durations[l] for l in labels])
max_duration = np.ceil(np.max(all_durations)) if len(all_durations) > 0 else 10
step = 0.1 #时间步长统计
bins = np.arange(0, max_duration + step, step)

# 为每个标签创建子图
for idx, label in enumerate(labels, 1):
    ax = plt.subplot(3, 1, idx)
    if not durations[label]:
        continue
    
    # 生成直方图数据
    counts, _ = np.histogram(durations[label], bins=bins)
    
    # 绘制柱状图
    bars = ax.bar(bins[:-1], counts, width=step, align='edge', 
                 edgecolor='black', alpha=0.7)
    
    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=8)
    
    # 设置图表属性
    ax.set_title(f'Label {label} time distribution ({len(durations[label])}files in total)')
    ax.set_xlabel('time(s)')
    ax.set_ylabel('count')
    ax.set_xticks(np.arange(0, max_duration + 1, 1))
    ax.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig('sta.png')