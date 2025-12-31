#!/usr/bin/env python3
"""
Analyze and compare three ProTracker replayer recordings.
"""

import wave
import struct
import sys
import math
from pathlib import Path

def load_wav(filename):
    """Load WAV file and return list of samples."""
    with wave.open(filename, 'rb') as wav:
        params = wav.getparams()
        frames = wav.readframes(params.nframes)

        # Convert to list of samples (16-bit stereo)
        samples = struct.unpack(f'{params.nframes * params.nchannels}h', frames)

        return samples, params

def calculate_rms(samples, channels=2):
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

def calculate_max_amplitude(samples, channels=2):
    """Calculate maximum amplitude for each channel."""
    max_amp = [0] * channels

    for ch in range(channels):
        for i in range(ch, len(samples), channels):
            max_amp[ch] = max(max_amp[ch], abs(samples[i]))

    return max_amp

def find_first_divergence(samples1, samples2, threshold=100):
    """Find first sample where recordings diverge beyond threshold."""
    min_len = min(len(samples1), len(samples2))

    for i in range(min_len):
        if abs(samples1[i] - samples2[i]) > threshold:
            # Convert to frame number (divide by 2 for stereo)
            return i // 2

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

def samples_to_time(sample_idx, sample_rate=44100):
    """Convert sample index to time string."""
    seconds = sample_idx / sample_rate
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}m {secs:.3f}s"

def main():
    print("=" * 80)
    print("ProTracker Replayer Audio Comparison")
    print("=" * 80)
    print()

    # Load all three recordings
    files = {
        'PT2.3F': 'pt23f_recording.wav',
        'HippoPlayer': 'hippoplayer_recording.wav',
        'LSPlayer': 'lsplayer_recording.wav'
    }

    recordings = {}
    params = {}

    print("Loading recordings...")
    for name, filename in files.items():
        if not Path(filename).exists():
            print(f"Error: {filename} not found!")
            return 1

        samples, param = load_wav(filename)
        recordings[name] = samples
        params[name] = param

        duration = len(samples) / param.framerate
        print(f"  {name:12s}: {len(samples):,} samples, {duration:.2f}s, "
              f"{param.nchannels} channels @ {param.framerate}Hz")

    print()

    # Basic statistics
    print("=" * 80)
    print("Basic Statistics")
    print("=" * 80)
    print()

    for name, samples in recordings.items():
        rms = calculate_rms(samples)
        max_amp = calculate_max_amplitude(samples)

        print(f"{name}:")
        print(f"  RMS (L/R):      {rms[0]:.2f} / {rms[1]:.2f}")
        print(f"  Max Amp (L/R):  {int(max_amp[0])} / {int(max_amp[1])}")
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

        # Calculate correlation
        correlation = calculate_correlation(samples1, samples2)

        # Find first divergence
        divergence_idx = find_first_divergence(samples1, samples2, threshold=100)

        # Calculate overall difference
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

        print(f"{name1} vs {name2}:")
        print(f"  Correlation:       {correlation:.6f}")
        print(f"  Mean difference:   {mean_diff:.2f}")
        print(f"  Max difference:    {max_diff:.2f}")

        if divergence_idx is not None:
            time_str = samples_to_time(divergence_idx)
            print(f"  First divergence:  Sample {divergence_idx:,} ({time_str})")
        else:
            print(f"  First divergence:  None detected (threshold=100)")

        # Calculate percentage of samples that differ significantly
        pct_diff = (significant_diff / min_len) * 100
        print(f"  Samples differing: {significant_diff:,} ({pct_diff:.2f}%)")
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
            print("  - PT2.3F differs from HippoPlayer")
        if not pt23_lsp_identical:
            print("  - PT2.3F differs from LSPlayer")
        if not hippo_lsp_identical:
            print("  - HippoPlayer differs from LSPlayer")

        print()
        print("  Recommended next steps:")
        print("  1. Visual inspection in Audacity")
        print("  2. Spectral analysis to identify frequency differences")
        print("  3. Generate difference audio files to hear the discrepancies")

    print()
    return 0

if __name__ == '__main__':
    sys.exit(main())
