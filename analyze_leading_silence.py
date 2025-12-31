#!/usr/bin/env python3
"""
Analyze WAV files for leading null samples at the binary level.
"""

import wave
import struct
import sys

def analyze_leading_samples(filename, num_samples=1000):
    """Analyze the first N samples of a WAV file."""
    with wave.open(filename, 'rb') as wav:
        params = wav.getparams()

        # Read first num_samples frames
        frames_to_read = min(num_samples, params.nframes)
        data = wav.readframes(frames_to_read)

        # Unpack as 16-bit signed integers
        samples = struct.unpack(f'{frames_to_read * params.nchannels}h', data)

        return samples, params

def find_first_nonzero(samples, threshold=0):
    """Find the first non-zero sample (or first sample above threshold)."""
    for i, sample in enumerate(samples):
        if abs(sample) > threshold:
            return i
    return None

def print_samples(filename):
    """Print detailed analysis of leading samples."""
    print(f"\n{'='*80}")
    print(f"Analyzing: {filename}")
    print(f"{'='*80}")

    samples, params = analyze_leading_samples(filename, 2000)

    print(f"Sample rate: {params.framerate} Hz")
    print(f"Channels: {params.nchannels}")
    print(f"Sample width: {params.sampwidth} bytes")
    print()

    # Find first non-zero sample (absolute value > 0)
    first_nonzero = find_first_nonzero(samples, threshold=0)

    # Find first significant sample (absolute value > 100)
    first_significant = find_first_nonzero(samples, threshold=100)

    if first_nonzero is not None:
        frame_nonzero = first_nonzero // params.nchannels
        time_nonzero = frame_nonzero / params.framerate
        print(f"First non-zero sample: index {first_nonzero} (frame {frame_nonzero}, {time_nonzero*1000:.3f}ms)")
    else:
        print("First non-zero sample: NONE in first 2000 samples")

    if first_significant is not None:
        frame_sig = first_significant // params.nchannels
        time_sig = frame_sig / params.framerate
        print(f"First significant sample (>100): index {first_significant} (frame {frame_sig}, {time_sig*1000:.3f}ms)")
    else:
        print("First significant sample: NONE in first 2000 samples")

    print()
    print("First 100 samples (left channel only):")
    print("Sample#  Value")
    print("-" * 40)

    # Print first 100 left channel samples
    for i in range(0, min(200, len(samples)), params.nchannels):
        frame_num = i // params.nchannels
        value = samples[i]

        if value != 0:
            print(f"{frame_num:6d}   {value:6d}  <-- FIRST NON-ZERO")
            # Print a few more after finding first non-zero
            for j in range(i + params.nchannels, min(i + 20*params.nchannels, len(samples)), params.nchannels):
                frame_num = j // params.nchannels
                print(f"{frame_num:6d}   {samples[j]:6d}")
            break

        if frame_num % 10 == 0:
            print(f"{frame_num:6d}   {value:6d}")

if __name__ == '__main__':
    files = [
        'pt23f_recording.wav',
        'hippoplayer_recording.wav',
        'lsplayer_recording.wav'
    ]

    for filename in files:
        print_samples(filename)

    print()
    print("="*80)
    print("Summary: If leading null samples are found, files should be trimmed")
    print("="*80)
