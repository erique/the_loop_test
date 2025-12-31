#!/usr/bin/env python3
"""
Analyze and compare three ProTracker replayer recordings (stdlib version).
Now supports 4-channel raw PCM files (16-bit signed, 96000Hz).
"""

import struct
import sys
import math
from pathlib import Path

def load_pcm(filename, sample_rate=96000, channels=4):
    """Load raw PCM file and return list of samples."""
    with open(filename, 'rb') as f:
        data = f.read()

    # Convert to list of samples (16-bit signed)
    num_samples = len(data) // 2
    samples = struct.unpack(f'{num_samples}h', data)

    return samples, sample_rate, channels

def calculate_rms(samples, channels=4):
    """Calculate RMS (Root Mean Square) for each channel."""
    rms = [0.0] * channels

    for ch in range(channels):
        sum_sq = 0
        count = 0
        for i in range(ch, len(samples), channels):
            sum_sq += samples[i] ** 2
            count += 1
        rms[ch] = math.sqrt(sum_sq / count) if count > 0 else 0

    return rms

def calculate_max_amplitude(samples, channels=4):
    """Calculate maximum amplitude for each channel."""
    max_amp = [0] * channels

    for ch in range(channels):
        for i in range(ch, len(samples), channels):
            max_amp[ch] = max(max_amp[ch], abs(samples[i]))

    return max_amp

def find_first_divergence(samples1, samples2, threshold=100, channels=4):
    """Find first sample where recordings diverge beyond threshold."""
    min_len = min(len(samples1), len(samples2))

    for i in range(min_len):
        if abs(samples1[i] - samples2[i]) > threshold:
            # Convert to frame number (divide by number of channels)
            return i // channels

    return None

def calculate_correlation(samples1, samples2):
    """Calculate correlation coefficient between two recordings."""
    min_len = min(len(samples1), len(samples2))

    # Calculate means
    mean1 = sum(samples1[:min_len]) / min_len
    mean2 = sum(samples2[:min_len]) / min_len

    # Calculate correlation
    numerator = 0
    sum_sq1 = 0
    sum_sq2 = 0

    for i in range(min_len):
        diff1 = samples1[i] - mean1
        diff2 = samples2[i] - mean2
        numerator += diff1 * diff2
        sum_sq1 += diff1 ** 2
        sum_sq2 += diff2 ** 2

    denominator = math.sqrt(sum_sq1 * sum_sq2)

    if denominator == 0:
        return 0

    return numerator / denominator

def calculate_per_channel_correlation(samples1, samples2, channels=4):
    """Calculate correlation for each channel separately."""
    correlations = []

    for ch in range(channels):
        # Extract channel samples
        ch_samples1 = [samples1[i] for i in range(ch, len(samples1), channels)]
        ch_samples2 = [samples2[i] for i in range(ch, len(samples2), channels)]

        corr = calculate_correlation(ch_samples1, ch_samples2)
        correlations.append(corr)

    return correlations

def samples_to_time(sample_idx, sample_rate=96000):
    """Convert sample index to time string."""
    seconds = sample_idx / sample_rate
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}m {secs:.3f}s"

def analyze_waveform_similarity(samples1, samples2, channels=4):
    """Perform detailed waveform similarity analysis."""
    min_len = min(len(samples1), len(samples2))

    # Overall statistics
    sum_diff = 0
    max_diff = 0
    significant_diff = 0

    for i in range(min_len):
        diff = abs(samples1[i] - samples2[i])
        sum_diff += diff
        max_diff = max(max_diff, diff)
        if diff > 100:
            significant_diff += 1

    mean_diff = sum_diff / min_len
    pct_significant = (significant_diff / min_len) * 100

    # Per-channel statistics
    per_channel = []
    for ch in range(channels):
        ch_sum_diff = 0
        ch_max_diff = 0
        ch_significant = 0
        ch_count = 0

        for i in range(ch, min_len, channels):
            diff = abs(samples1[i] - samples2[i])
            ch_sum_diff += diff
            ch_max_diff = max(ch_max_diff, diff)
            if diff > 100:
                ch_significant += 1
            ch_count += 1

        per_channel.append({
            'mean': ch_sum_diff / ch_count if ch_count > 0 else 0,
            'max': ch_max_diff,
            'pct_significant': (ch_significant / ch_count * 100) if ch_count > 0 else 0
        })

    return {
        'mean': mean_diff,
        'max': max_diff,
        'pct_significant': pct_significant,
        'per_channel': per_channel
    }

def main():
    print("=" * 80)
    print("ProTracker Replayer Audio Comparison (4-Channel Raw PCM, stdlib)")
    print("=" * 80)
    print()

    # Load all three recordings
    files = {
        'PT2.3F': 'pt23f_channels_raw.pcm',
        'HippoPlayer': 'hippoplayer_channels_raw.pcm',
        'LSPlayer': 'lsplayer_channels_raw.pcm'
    }

    recordings = {}
    params = {}
    sample_rate = 96000
    channels = 4

    print("Loading recordings...")
    for name, filename in files.items():
        if not Path(filename).exists():
            print(f"Error: {filename} not found!")
            return 1

        samples, sr, ch = load_pcm(filename)
        recordings[name] = samples
        params[name] = {'sample_rate': sr, 'channels': ch}

        num_frames = len(samples) // ch
        duration = num_frames / sr
        print(f"  {name:12s}: {len(samples):,} samples ({num_frames:,} frames), {duration:.2f}s, "
              f"{ch} channels @ {sr}Hz")

    print()

    # Basic statistics
    print("=" * 80)
    print("Basic Statistics (Per Channel)")
    print("=" * 80)
    print()

    for name, samples in recordings.items():
        rms = calculate_rms(samples, channels)
        max_amp = calculate_max_amplitude(samples, channels)

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

        # Calculate correlation
        correlation = calculate_correlation(samples1, samples2)
        per_ch_corr = calculate_per_channel_correlation(samples1, samples2, channels)

        # Find first divergence
        divergence_idx = find_first_divergence(samples1, samples2, threshold=100, channels=channels)

        # Detailed analysis
        analysis = analyze_waveform_similarity(samples1, samples2, channels)

        print(f"{name1} vs {name2}:")
        print(f"  Overall correlation:    {correlation:.6f}")
        print(f"  Per-channel correlation: Ch0={per_ch_corr[0]:.6f}  Ch1={per_ch_corr[1]:.6f}  "
              f"Ch2={per_ch_corr[2]:.6f}  Ch3={per_ch_corr[3]:.6f}")
        print(f"  Mean difference:        {analysis['mean']:.2f}")
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
    pt23_hippo_identical = calculate_correlation(recordings['PT2.3F'], recordings['HippoPlayer']) > 0.9999
    pt23_lsp_identical = calculate_correlation(recordings['PT2.3F'], recordings['LSPlayer']) > 0.9999
    hippo_lsp_identical = calculate_correlation(recordings['HippoPlayer'], recordings['LSPlayer']) > 0.9999

    if pt23_hippo_identical and pt23_lsp_identical and hippo_lsp_identical:
        print("✓ All three recordings are effectively identical (correlation > 0.9999)")
        print("  No significant playback differences detected.")
    else:
        print("✗ Recordings show differences:")
        if not pt23_hippo_identical:
            corr = calculate_correlation(recordings['PT2.3F'], recordings['HippoPlayer'])
            print(f"  - PT2.3F differs from HippoPlayer (corr: {corr:.6f})")
        if not pt23_lsp_identical:
            corr = calculate_correlation(recordings['PT2.3F'], recordings['LSPlayer'])
            print(f"  - PT2.3F differs from LSPlayer (corr: {corr:.6f})")
        if not hippo_lsp_identical:
            corr = calculate_correlation(recordings['HippoPlayer'], recordings['LSPlayer'])
            print(f"  - HippoPlayer differs from LSPlayer (corr: {corr:.6f})")

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
