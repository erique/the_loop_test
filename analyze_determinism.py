#!/Users/erik/src/the_loop_test/venv/bin/python
"""
Analyze determinism of FS-UAE by comparing multiple recordings of the same replayer.
Should show 1.0 correlation if perfectly deterministic.
"""

import sys
import numpy as np
from pathlib import Path

def load_pcm(filename, sample_rate=96000, channels=4):
    """Load raw PCM file and return numpy array of samples."""
    with open(filename, 'rb') as f:
        data = f.read()
    samples = np.frombuffer(data, dtype=np.int16)
    samples = samples.reshape(-1, channels)
    return samples, sample_rate

def calculate_correlation(samples1, samples2):
    """Calculate correlation coefficient between two recordings."""
    s1_flat = samples1.flatten()
    s2_flat = samples2.flatten()
    correlation = np.corrcoef(s1_flat, s2_flat)[0, 1]
    return correlation

def calculate_per_channel_correlation(samples1, samples2):
    """Calculate correlation for each channel separately."""
    correlations = []
    for ch in range(samples1.shape[1]):
        corr = np.corrcoef(samples1[:, ch], samples2[:, ch])[0, 1]
        correlations.append(corr)
    return correlations

def find_first_difference(samples1, samples2):
    """Find first sample where recordings differ."""
    min_len = min(len(samples1), len(samples2))
    samples1 = samples1[:min_len]
    samples2 = samples2[:min_len]
    
    diff = samples1 != samples2
    diff_mask = np.any(diff, axis=1)
    diff_points = np.where(diff_mask)[0]
    
    if len(diff_points) > 0:
        return diff_points[0]
    return None

def samples_to_time(sample_idx, sample_rate=96000):
    """Convert sample index to time string."""
    seconds = sample_idx / sample_rate
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}m {secs:.3f}s"

def main():
    print("=" * 80)
    print("FS-UAE Determinism Analysis")
    print("=" * 80)
    print()

    # Load all three takes
    files = {
        'Take 1': 'hippoplayer_channels_raw_take1.pcm',
        'Take 2': 'hippoplayer_channels_raw_take2.pcm',
        'Take 3': 'hippoplayer_channels_raw_take3.pcm'
    }

    recordings = {}
    sample_rate = 96000

    print("Loading recordings...")
    for name, filename in files.items():
        if not Path(filename).exists():
            print(f"Error: {filename} not found!")
            return 1

        samples, sr = load_pcm(filename)
        recordings[name] = samples

        duration = len(samples) / sr
        print(f"  {name:8s}: {len(samples):,} frames, {duration:.2f}s, "
              f"{samples.shape[1]} channels @ {sr}Hz")

    print()

    # Check if recordings are identical
    print("=" * 80)
    print("Determinism Check")
    print("=" * 80)
    print()

    comparisons = [
        ('Take 1', 'Take 2'),
        ('Take 1', 'Take 3'),
        ('Take 2', 'Take 3')
    ]

    all_identical = True

    for name1, name2 in comparisons:
        samples1 = recordings[name1]
        samples2 = recordings[name2]

        # Ensure same length
        min_len = min(len(samples1), len(samples2))
        samples1_cmp = samples1[:min_len]
        samples2_cmp = samples2[:min_len]

        # Check if exactly identical
        are_identical = np.array_equal(samples1_cmp, samples2_cmp)

        # Calculate correlation
        correlation = calculate_correlation(samples1_cmp, samples2_cmp)
        per_ch_corr = calculate_per_channel_correlation(samples1_cmp, samples2_cmp)

        # Find first difference
        first_diff = find_first_difference(samples1_cmp, samples2_cmp)

        # Count differences
        diff = samples1_cmp != samples2_cmp
        num_diffs = np.sum(diff)
        total_samples = samples1_cmp.size
        pct_diff = (num_diffs / total_samples) * 100

        print(f"{name1} vs {name2}:")
        print(f"  Exactly identical:      {are_identical}")
        print(f"  Overall correlation:    {correlation:.10f}")
        print(f"  Per-channel correlation: Ch0={per_ch_corr[0]:.10f}  Ch1={per_ch_corr[1]:.10f}  "
              f"Ch2={per_ch_corr[2]:.10f}  Ch3={per_ch_corr[3]:.10f}")
        
        if first_diff is not None:
            time_str = samples_to_time(first_diff, sample_rate)
            print(f"  First difference:       Frame {first_diff:,} ({time_str})")
        else:
            print(f"  First difference:       None")
        
        print(f"  Different samples:      {num_diffs:,} / {total_samples:,} ({pct_diff:.4f}%)")
        print()

        if not are_identical:
            all_identical = False

    # Overall assessment
    print("=" * 80)
    print("Assessment")
    print("=" * 80)
    print()

    if all_identical:
        print("✓ FS-UAE is PERFECTLY DETERMINISTIC")
        print("  All three recordings are byte-for-byte identical.")
    else:
        print("✗ FS-UAE is NOT DETERMINISTIC")
        print("  Recordings differ between runs.")
        print()
        print("  This means comparison results may vary between recording sessions.")

    print()
    return 0

if __name__ == '__main__':
    sys.exit(main())
