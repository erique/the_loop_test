#!/usr/bin/env python3
"""
Find the exact first non-zero sample in WAV files.
"""

import wave
import struct

def find_first_nonzero_frame(filename):
    """Find the exact frame where audio starts."""
    with wave.open(filename, 'rb') as wav:
        params = wav.getparams()
        chunk_size = params.framerate * 10  # 10 second chunks

        frame = 0
        while frame < params.nframes:
            wav.setpos(frame)
            data = wav.readframes(min(chunk_size, params.nframes - frame))

            if not data:
                break

            samples = struct.unpack(f'{len(data)//2}h', data)

            # Find first non-zero sample in this chunk
            for i, sample in enumerate(samples):
                if sample != 0:
                    # Found it, return frame number
                    first_frame = frame + (i // params.nchannels)
                    return first_frame, params

            frame += chunk_size

        return None, params

if __name__ == '__main__':
    files = [
        'pt23f_recording.wav',
        'hippoplayer_recording.wav',
        'lsplayer_recording.wav'
    ]

    print("Finding exact audio start for each file...")
    print()

    results = []
    for filename in files:
        first_frame, params = find_first_nonzero_frame(filename)

        if first_frame is not None:
            time_sec = first_frame / params.framerate
            time_ms = time_sec * 1000

            print(f"{filename:25s}:")
            print(f"  First non-zero frame: {first_frame}")
            print(f"  Time: {time_sec:.6f}s ({time_ms:.3f}ms)")
            print()

            results.append((filename, first_frame, time_sec))
        else:
            print(f"{filename:25s}: NO AUDIO FOUND!")
            print()

    # Generate trimming commands
    if results:
        print("\n" + "="*80)
        print("To trim the null samples, use these ffmpeg commands:")
        print("="*80)
        print()

        for filename, first_frame, time_sec in results:
            output_name = filename.replace('.wav', '_trimmed.wav')
            print(f"# Trim {filename}")
            print(f"ffmpeg -i {filename} -af \"atrim=start_sample={first_frame}\" {output_name} -y")
            print()
