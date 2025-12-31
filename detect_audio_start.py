#!/usr/bin/env python3
"""
Detect where audio starts in a WAV file (first non-silent sample).
"""

import wave
import struct
import sys

def find_audio_start(filename, threshold=300):
    """Find the first frame where audio exceeds threshold."""
    with wave.open(filename, 'rb') as wav:
        params = wav.getparams()
        chunk_size = params.framerate  # 1 second chunks

        frame = 0
        while frame < params.nframes:
            wav.setpos(frame)
            data = wav.readframes(min(chunk_size, params.nframes - frame))

            if not data:
                break

            samples = struct.unpack(f'{len(data)//2}h', data)

            # Check if any sample in this chunk exceeds threshold
            for i, sample in enumerate(samples):
                if abs(sample) > threshold:
                    # Found audio, return frame number
                    return frame + (i // params.nchannels)

            frame += chunk_size

        return None

if __name__ == '__main__':
    files = ['pt23f_recording.wav', 'hippoplayer_recording.wav', 'lsplayer_recording.wav']

    for filename in files:
        start_frame = find_audio_start(filename)

        with wave.open(filename, 'rb') as wav:
            params = wav.getparams()
            start_time = start_frame / params.framerate if start_frame else 0

        print(f"{filename:25s}: audio starts at frame {start_frame:6d} ({start_time:.3f}s)")
