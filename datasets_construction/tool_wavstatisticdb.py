import os
import re
import numpy as np
import matplotlib.pyplot as plt
import librosa

def parse_label(filename):
    """Extract label from filename"""
    match = re.search(r'_label(\d)\.wav$', filename)
    return match.group(1) if match else None

def calculate_peak(y):
    """Calculate raw peak value"""
    return np.max(np.abs(y))

# Configuration
BASE_DIR = 'data/all'
LABELS = ['0', '1', '2']
STEP = 0.001  # 可调节步长参数
SAVE_PATH = 'sta_db.png'

# Initialize data storage
peak_values = {label: [] for label in LABELS}

# Process files
for filename in os.listdir(BASE_DIR):
    if filename.endswith('.wav'):
        label = parse_label(filename)
        if label not in LABELS:
            continue
        
        file_path = os.path.join(BASE_DIR, filename)
        try:
            y, _ = librosa.load(file_path, sr=None, mono=True)
            peak = calculate_peak(y)
            # if peak <=0.1: #低通滤波
            #     peak_values[label].append(peak)
            peak_values[label].append(peak)
        except Exception as e:
            print(f"Error processing {filename}: {e}")

# Visualization setup
plt.figure(figsize=(10, 12), dpi=100)
all_peaks = np.concatenate(list(peak_values.values()))
max_value = np.max(all_peaks) if len(all_peaks) > 0 else 1.0
bins = np.arange(0, max_value + STEP, STEP)

# Create subplots
for idx, label in enumerate(LABELS, 1):
    ax = plt.subplot(3, 1, idx)
    current_values = peak_values[label]
    if not current_values:
        continue
    
    # Generate histogram
    counts, _ = np.histogram(current_values, bins=bins)
    # counts, _ = np.histogram(current_values, bins=bins,range=(0,0.3))
    
    # Create bars
    bars = ax.bar(bins[:-1], counts, width=STEP*0.9, align='edge',
                 color='#2ca02c', edgecolor='black', alpha=0.8)
    
    # Add value labels
    for bar in bars:
        if (height := bar.get_height()) > 0:
            ax.text(bar.get_x() + bar.get_width()/2, height,
                    f'{int(height)}', ha='center', va='bottom', fontsize=8)
    
    # Axis settings
    ax.set_title(f'Label {label} Peak Distribution (N={len(current_values)})', pad=12)
    ax.set_xlabel('Peak Value')
    ax.set_ylabel('Count')
    
    # 智能刻度设置
    major_step = max(5*STEP,0.1)
    ax.set_xticks(np.arange(0, max_value + major_step, major_step))
    ax.set_xlim(0, max_value + STEP)
    ax.grid(axis='y', linestyle=':', alpha=0.5)
    # ax.set_xlim(0,0.3)


plt.tight_layout()
plt.savefig(SAVE_PATH, bbox_inches='tight', dpi=300)
print(f"Saved to {SAVE_PATH}")