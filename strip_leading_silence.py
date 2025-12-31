#!/usr/bin/env python3
"""
Strip leading silence from raw 4-channel PCM audio.

Usage: ./strip_leading_silence.py input.pcm output.pcm
       ./strip_leading_silence.py input.pcm output.pcm --threshold 100

Reads raw PCM data (16-bit signed little-endian, 4 channels interleaved)
and removes all leading frames where all 4 channels are below the threshold.
"""

import sys
import struct
import os

def strip_leading_silence(input_file, output_file, threshold=0):
    """
    Strip leading silence from 4-channel raw PCM file.

    Args:
        input_file: Path to input .pcm file
        output_file: Path to output .pcm file
        threshold: Absolute value threshold (default 0 = perfect silence)
    """
    # Read the entire file
    with open(input_file, 'rb') as f:
        data = f.read()

    # Each sample is 2 bytes (int16), 4 channels = 8 bytes per frame
    bytes_per_frame = 8
    num_frames = len(data) // bytes_per_frame

    print(f"Input file: {input_file}")
    print(f"File size: {len(data)} bytes")
    print(f"Total frames: {num_frames}")
    print(f"Threshold: {threshold}")
    print()

    # Find the first non-silent frame
    first_sound = None
    for i in range(num_frames):
        offset = i * bytes_per_frame
        # Unpack 4 int16 samples (little-endian)
        ch0, ch1, ch2, ch3 = struct.unpack_from('<hhhh', data, offset)

        # Check if any channel exceeds threshold
        if (abs(ch0) > threshold or abs(ch1) > threshold or
            abs(ch2) > threshold or abs(ch3) > threshold):
            first_sound = i
            if i < 10:
                print(f"First sound at frame {i}: ch0={ch0} ch1={ch1} ch2={ch2} ch3={ch3}")
            break

        # Show progress for large files
        if i > 0 and i % 100000 == 0:
            print(f"Scanning... {i}/{num_frames} frames ({i*100//num_frames}%)", end='\r')

    if first_sound is None:
        print("WARNING: No sound detected in entire file!")
        print("File contains only silence.")
        return

    # Calculate statistics
    silent_frames = first_sound
    silent_bytes = silent_frames * bytes_per_frame
    silent_seconds = silent_frames / 96000.0  # Assuming 96kHz sample rate

    print(f"Leading silence: {silent_frames} frames ({silent_bytes} bytes, {silent_seconds:.3f} seconds)")
    print(f"Keeping {num_frames - silent_frames} frames from position {first_sound}")

    # Write non-silent portion to output file
    output_data = data[silent_frames * bytes_per_frame:]
    with open(output_file, 'wb') as f:
        f.write(output_data)

    print(f"\nOutput file: {output_file}")
    print(f"Output size: {len(output_data)} bytes")
    print(f"Removed {silent_bytes} bytes of leading silence")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Optional threshold argument
    threshold = 0
    if len(sys.argv) >= 4 and sys.argv[3] == '--threshold':
        if len(sys.argv) >= 5:
            threshold = int(sys.argv[4])
        else:
            print("Error: --threshold requires a value")
            sys.exit(1)
    elif len(sys.argv) >= 4:
        try:
            threshold = int(sys.argv[3])
        except ValueError:
            pass

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)

    strip_leading_silence(input_file, output_file, threshold)
