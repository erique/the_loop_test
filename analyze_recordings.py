#!/usr/bin/env python3
"""
Analyze and compare three ProTracker replayer recordings using NumPy.
"""

import wave
import struct
import sys
import numpy as np
from pathlib import Path

def load_wav(filename):
    """Load WAV file and return numpy array of samples."""
    with wave.open(filename, 'rb') as wav:
        params = wav.getparams()
        frames = wav.readframes(params.nframes)

        # Convert to numpy array (16-bit stereo)
        samples = np.frombuffer(frames, dtype=np.int16)

        # Reshape to (frames, channels)
        samples = samples.reshape(-1, params.nchannels)

        return samples, params

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

def samples_to_time(sample_idx, sample_rate=44100):
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

    return {
        'mean': mean_diff,
        'median': median_diff,
        'std': std_diff,
        'max': max_diff,
        'pct_significant': pct_significant
    }

def main():
    print("=" * 80)
    print("ProTracker Replayer Audio Comparison (NumPy)")
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
        print(f"  {name:12s}: {len(samples):,} frames, {duration:.2f}s, "
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
        samples1 = samples1[:min_len]
        samples2 = samples2[:min_len]

        # Calculate correlation
        correlation = calculate_correlation(samples1, samples2)

        # Find first divergence
        divergence_idx = find_first_divergence(samples1, samples2, threshold=100)

        # Detailed analysis
        analysis = analyze_waveform_similarity(samples1, samples2)

        print(f"{name1} vs {name2}:")
        print(f"  Correlation:       {correlation:.6f}")
        print(f"  Mean difference:   {analysis['mean']:.2f}")
        print(f"  Median difference: {analysis['median']:.2f}")
        print(f"  Std deviation:     {analysis['std']:.2f}")
        print(f"  Max difference:    {analysis['max']:.2f}")

        if divergence_idx is not None:
            time_str = samples_to_time(divergence_idx)
            print(f"  First divergence:  Frame {divergence_idx:,} ({time_str})")
        else:
            print(f"  First divergence:  None detected (threshold=100)")

        print(f"  Significant diffs: {analysis['pct_significant']:.2f}% of samples")
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
        print("  1. Visual inspection in Audacity")
        print("  2. Spectral analysis to identify frequency differences")
        print("  3. Listen to generated difference audio files (*_diff.wav)")

    print()
    return 0

if __name__ == '__main__':
    sys.exit(main())
