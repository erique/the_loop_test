#!/Users/erik/src/the_loop_test/venv/bin/python
"""
Generate per-channel difference files between ProTracker replayer recordings.
Creates difference files for each channel that can be visualized or played back.

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

def save_pcm_4channel(filename, samples):
    """Save 4-channel interleaved PCM (16-bit signed)."""
    # Ensure int16 type and save (samples should be shape [frames, 4])
    samples = samples.astype(np.int16)
    with open(filename, 'wb') as f:
        f.write(samples.tobytes())

def generate_diffs(name1, file1, name2, file2):
    """Generate per-channel difference files between two recordings."""
    print(f"\n{'='*80}")
    print(f"Generating diffs: {name1} vs {name2}")
    print(f"{'='*80}\n")

    # Load both recordings
    samples1, sr = load_pcm(file1)
    samples2, sr = load_pcm(file2)

    # Use minimum length
    min_len = min(len(samples1), len(samples2))
    samples1 = samples1[:min_len]
    samples2 = samples2[:min_len]

    print(f"Loaded {min_len:,} frames ({min_len/sr:.2f}s)\n")

    # Calculate difference for all channels
    diff = samples1.astype(np.int32) - samples2.astype(np.int32)

    # Clip to int16 range
    diff_clipped = np.clip(diff, -32768, 32767).astype(np.int16)

    # Calculate per-channel statistics
    diff_stats = []

    for ch in range(4):
        ch_diff = diff[:, ch]

        # Statistics
        mean_abs_diff = np.mean(np.abs(ch_diff))
        max_abs_diff = np.max(np.abs(ch_diff))
        rms_diff = np.sqrt(np.mean(ch_diff.astype(np.float64)**2))

        # Count significant differences
        significant = np.sum(np.abs(ch_diff) > 100)
        pct_significant = (significant / len(ch_diff)) * 100

        diff_stats.append({
            'channel': ch,
            'mean_abs': mean_abs_diff,
            'max_abs': max_abs_diff,
            'rms': rms_diff,
            'pct_significant': pct_significant
        })

        print(f"Channel {ch}:")
        print(f"  Mean abs diff: {mean_abs_diff:7.2f}")
        print(f"  Max abs diff:  {max_abs_diff:7.0f}")
        print(f"  RMS diff:      {rms_diff:7.2f}")
        print(f"  Significant:   {pct_significant:6.2f}% (>{100})")
        print()

    # Save 4-channel diff as single PCM file
    prefix = f"{name1.lower()}_vs_{name2.lower()}"
    diff_filename = f"{prefix}_diff.pcm"
    save_pcm_4channel(diff_filename, diff_clipped)
    print(f"Saved 4-channel diff: {diff_filename}\n")

    # Summary
    print(f"{'='*80}")
    print("Summary:")
    print(f"{'='*80}\n")

    # Find most/least different channels
    by_rms = sorted(diff_stats, key=lambda x: x['rms'])
    print(f"Least different: Channel {by_rms[0]['channel']} (RMS={by_rms[0]['rms']:.2f})")
    print(f"Most different:  Channel {by_rms[-1]['channel']} (RMS={by_rms[-1]['rms']:.2f})")
    print()

    # Conversion examples
    print("To convert 4-channel diff to WAV:")
    print(f"  ffmpeg -f s16le -ar 96000 -ac 4 -i {prefix}_diff.pcm {prefix}_diff.wav")
    print()
    print("To extract individual channels:")
    print(f"  ffmpeg -f s16le -ar 96000 -ac 4 -i {prefix}_diff.pcm -filter_complex \\")
    print(f"    \"channelsplit=channel_layout=quad[c0][c1][c2][c3]\" \\")
    print(f"    -map \"[c0]\" {prefix}_ch0_diff.wav -map \"[c1]\" {prefix}_ch1_diff.wav \\")
    print(f"    -map \"[c2]\" {prefix}_ch2_diff.wav -map \"[c3]\" {prefix}_ch3_diff.wav")
    print()
    print("To amplify all channels for easier hearing (10x gain):")
    print(f"  ffmpeg -f s16le -ar 96000 -ac 4 -i {prefix}_diff.pcm -filter:a \"volume=10\" {prefix}_diff_10x.wav")
    print()

def main():
    print("="*80)
    print("Per-Channel Difference Generator")
    print("="*80)

    # Define comparisons
    files = {
        'PT2.3F': 'pt23f_channels_raw.pcm',
        'HippoPlayer': 'hippoplayer_channels_raw.pcm',
        'LSPlayer': 'lsplayer_channels_raw.pcm'
    }

    # Check files exist
    for name, filename in files.items():
        if not Path(filename).exists():
            print(f"Error: {filename} not found!")
            return 1

    # Generate all pairwise diffs
    comparisons = [
        ('PT2.3F', 'HippoPlayer'),
        ('PT2.3F', 'LSPlayer'),
        ('HippoPlayer', 'LSPlayer')
    ]

    for name1, name2 in comparisons:
        generate_diffs(name1, files[name1], name2, files[name2])

    print("\nDone! All 4-channel difference files generated.")
    return 0

if __name__ == '__main__':
    sys.exit(main())
