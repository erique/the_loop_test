#!/Users/erik/src/the_loop_test/venv/bin/python
"""
Analyze and compare three ProTracker replayer recordings using NumPy.
Now supports 4-channel raw PCM files (16-bit signed, 96000Hz).

Requirements:
  - NumPy (install in venv)

To initialize venv:
  python3 -m venv venv
  ./venv/bin/pip install numpy
"""

import struct
import sys
import numpy as np
from pathlib import Path

def load_pcm(filename, sample_rate=96000, channels=4):
    """Load raw PCM file and return numpy array of samples."""
    with open(filename, 'rb') as f:
        data = f.read()

    # Convert to numpy array (16-bit signed)
    samples = np.frombuffer(data, dtype=np.int16)

    # Reshape to (frames, channels)
    samples = samples.reshape(-1, channels)

    return samples, sample_rate

def calculate_rms(samples):
    """Calculate RMS (Root Mean Square) for each channel."""
    return np.sqrt(np.mean(samples.astype(np.float64)**2, axis=0))

def calculate_max_amplitude(samples):
    """Calculate maximum amplitude for each channel."""
    return np.max(np.abs(samples), axis=0)

def find_first_divergence(samples1, samples2, threshold=100):
    """Find first sample where recordings diverge beyond threshold."""
    diff = np.abs(samples1 - samples2)
    divergence_mask = np.any(diff > threshold, axis=1)
    divergence_points = np.where(divergence_mask)[0]

    if len(divergence_points) > 0:
        return divergence_points[0]
    return None

def calculate_correlation(samples1, samples2):
    """Calculate correlation coefficient between two recordings."""
    # Flatten to 1D for correlation
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

def samples_to_time(sample_idx, sample_rate=96000):
    """Convert sample index to time string."""
    seconds = sample_idx / sample_rate
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}m {secs:.3f}s"

def analyze_waveform_similarity(samples1, samples2):
    """Perform detailed waveform similarity analysis."""
    min_len = min(len(samples1), len(samples2))
    s1 = samples1[:min_len]
    s2 = samples2[:min_len]

    # Calculate absolute differences
    diff = np.abs(s1 - s2)

    # Statistics
    mean_diff = np.mean(diff)
    median_diff = np.median(diff)
    std_diff = np.std(diff)
    max_diff = np.max(diff)

    # Percentage of samples with significant differences (> 100)
    significant_mask = np.any(diff > 100, axis=1)
    pct_significant = (np.sum(significant_mask) / len(s1)) * 100

    # Per-channel statistics
    per_channel = []
    for ch in range(s1.shape[1]):
        ch_diff = diff[:, ch]
        per_channel.append({
            'mean': np.mean(ch_diff),
            'max': np.max(ch_diff),
            'pct_significant': (np.sum(ch_diff > 100) / len(ch_diff)) * 100
        })

    return {
        'mean': mean_diff,
        'median': median_diff,
        'std': std_diff,
        'max': max_diff,
        'pct_significant': pct_significant,
        'per_channel': per_channel
    }

def main():
    print("=" * 80)
    print("ProTracker Replayer Audio Comparison (4-Channel Raw PCM, NumPy)")
    print("=" * 80)
    print()

    # Load all three recordings
    files = {
        'PT2.3F': 'pt23f_channels_raw.pcm',
        'HippoPlayer': 'hippoplayer_channels_raw.pcm',
        'LSPlayer': 'lsplayer_channels_raw.pcm'
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
        print(f"  {name:12s}: {len(samples):,} frames, {duration:.2f}s, "
              f"{samples.shape[1]} channels @ {sr}Hz")

    print()

    # Basic statistics
    print("=" * 80)
    print("Basic Statistics (Per Channel)")
    print("=" * 80)
    print()

    for name, samples in recordings.items():
        rms = calculate_rms(samples)
        max_amp = calculate_max_amplitude(samples)

        print(f"{name}:")
        print(f"  RMS:     Ch0={rms[0]:7.2f}  Ch1={rms[1]:7.2f}  Ch2={rms[2]:7.2f}  Ch3={rms[3]:7.2f}")
        print(f"  Max Amp: Ch0={int(max_amp[0]):5d}  Ch1={int(max_amp[1]):5d}  Ch2={int(max_amp[2]):5d}  Ch3={int(max_amp[3]):5d}")
        print()

    # Pairwise comparisons
    print("=" * 80)
    print("Pairwise Comparisons")
    print("=" * 80)
    print()

    comparisons = [
        ('PT2.3F', 'HippoPlayer'),
        ('PT2.3F', 'LSPlayer'),
        ('HippoPlayer', 'LSPlayer')
    ]

    for name1, name2 in comparisons:
        samples1 = recordings[name1]
        samples2 = recordings[name2]

        # Ensure same length
        min_len = min(len(samples1), len(samples2))
        samples1 = samples1[:min_len]
        samples2 = samples2[:min_len]

        # Calculate correlation
        correlation = calculate_correlation(samples1, samples2)
        per_ch_corr = calculate_per_channel_correlation(samples1, samples2)

        # Find first divergence
        divergence_idx = find_first_divergence(samples1, samples2, threshold=100)

        # Detailed analysis
        analysis = analyze_waveform_similarity(samples1, samples2)

        print(f"{name1} vs {name2}:")
        print(f"  Overall correlation:    {correlation:.6f}")
        print(f"  Per-channel correlation: Ch0={per_ch_corr[0]:.6f}  Ch1={per_ch_corr[1]:.6f}  "
              f"Ch2={per_ch_corr[2]:.6f}  Ch3={per_ch_corr[3]:.6f}")
        print(f"  Mean difference:        {analysis['mean']:.2f}")
        print(f"  Median difference:      {analysis['median']:.2f}")
        print(f"  Std deviation:          {analysis['std']:.2f}")
        print(f"  Max difference:         {analysis['max']:.2f}")

        if divergence_idx is not None:
            time_str = samples_to_time(divergence_idx, sample_rate)
            print(f"  First divergence:       Frame {divergence_idx:,} ({time_str})")
        else:
            print(f"  First divergence:       None detected (threshold=100)")

        print(f"  Significant diffs:      {analysis['pct_significant']:.2f}% of samples")

        # Per-channel differences
        print(f"  Per-channel mean diff:  Ch0={analysis['per_channel'][0]['mean']:.2f}  "
              f"Ch1={analysis['per_channel'][1]['mean']:.2f}  "
              f"Ch2={analysis['per_channel'][2]['mean']:.2f}  "
              f"Ch3={analysis['per_channel'][3]['mean']:.2f}")
        print(f"  Per-channel max diff:   Ch0={analysis['per_channel'][0]['max']:.0f}  "
              f"Ch1={analysis['per_channel'][1]['max']:.0f}  "
              f"Ch2={analysis['per_channel'][2]['max']:.0f}  "
              f"Ch3={analysis['per_channel'][3]['max']:.0f}")
        print()

    # Overall assessment
    print("=" * 80)
    print("Overall Assessment")
    print("=" * 80)
    print()

    # Check if all three are identical
    pt23_hippo_corr = calculate_correlation(
        recordings['PT2.3F'][:min(len(recordings['PT2.3F']), len(recordings['HippoPlayer']))],
        recordings['HippoPlayer'][:min(len(recordings['PT2.3F']), len(recordings['HippoPlayer']))]
    )
    pt23_lsp_corr = calculate_correlation(
        recordings['PT2.3F'][:min(len(recordings['PT2.3F']), len(recordings['LSPlayer']))],
        recordings['LSPlayer'][:min(len(recordings['PT2.3F']), len(recordings['LSPlayer']))]
    )
    hippo_lsp_corr = calculate_correlation(
        recordings['HippoPlayer'][:min(len(recordings['HippoPlayer']), len(recordings['LSPlayer']))],
        recordings['LSPlayer'][:min(len(recordings['HippoPlayer']), len(recordings['LSPlayer']))]
    )

    threshold = 0.9999

    if pt23_hippo_corr > threshold and pt23_lsp_corr > threshold and hippo_lsp_corr > threshold:
        print(f"✓ All three recordings are effectively identical (correlation > {threshold})")
        print("  No significant playback differences detected.")
    else:
        print("✗ Recordings show significant differences:")
        if pt23_hippo_corr <= threshold:
            print(f"  - PT2.3F differs from HippoPlayer (corr: {pt23_hippo_corr:.6f})")
        if pt23_lsp_corr <= threshold:
            print(f"  - PT2.3F differs from LSPlayer (corr: {pt23_lsp_corr:.6f})")
        if hippo_lsp_corr <= threshold:
            print(f"  - HippoPlayer differs from LSPlayer (corr: {hippo_lsp_corr:.6f})")

        print()
        print("  Recommended next steps:")
        print("  1. Convert to WAV for visual inspection:")
        print("     ffmpeg -f s16le -ar 96000 -ac 4 -i <file>.pcm <file>.wav")
        print("  2. Extract individual channels for analysis:")
        print("     ffmpeg -f s16le -ar 96000 -ac 4 -i <file>.pcm -filter_complex \\")
        print("       \"channelsplit=channel_layout=quad[c0][c1][c2][c3]\" \\")
        print("       -map \"[c0]\" ch0.wav -map \"[c1]\" ch1.wav \\")
        print("       -map \"[c2]\" ch2.wav -map \"[c3]\" ch3.wav")

    print()
    return 0

if __name__ == '__main__':
    sys.exit(main())
