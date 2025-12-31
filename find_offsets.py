#!/usr/bin/env python3
"""
Find audio segment offsets by detecting silence/loudness.
"""

import wave
import struct
import sys

def load_wav_chunk(filename, start_frame=0, num_frames=44100):
    """Load a chunk of WAV file."""
    with wave.open(filename, 'rb') as wav:
        params = wav.getparams()

        if start_frame > 0:
            wav.setpos(start_frame)

        frames = wav.readframes(min(num_frames, params.nframes - start_frame))
        samples = struct.unpack(f'{len(frames)//2}h', frames)

        return samples, params

def calculate_rms_window(filename, window_size=44100):
    """Calculate RMS for consecutive windows across the file."""
    with wave.open(filename, 'rb') as wav:
        params = wav.getparams()
        total_frames = params.nframes

        print(f"File: {filename}")
        print(f"Duration: {total_frames / params.framerate:.2f} seconds")
        print(f"Analyzing with {window_size/params.framerate:.1f}s windows...")
        print()
        print("Time(s)  RMS     State")
        print("-" * 40)

        frame = 0
        results = []

        while frame < total_frames:
            samples, _ = load_wav_chunk(filename, frame, window_size)

            # Calculate RMS
            if len(samples) > 0:
                rms = (sum(s**2 for s in samples) / len(samples)) ** 0.5
            else:
                rms = 0

            time_sec = frame / params.framerate

            # Classify as silence or audio
            state = "AUDIO" if rms > 500 else "silence"

            results.append((time_sec, rms, state))
            print(f"{time_sec:6.1f}   {rms:6.0f}  {state}")

            frame += window_size

        print()

        # Find transitions
        print("Detected transitions:")
        print("-" * 40)

        for i in range(1, len(results)):
            prev_state = results[i-1][2]
            curr_state = results[i][2]

            if prev_state != curr_state:
                time_sec = results[i][0]
                minutes = int(time_sec // 60)
                seconds = time_sec % 60
                print(f"{time_sec:6.1f}s ({minutes}m {seconds:04.1f}s): {prev_state} -> {curr_state}")

        return results

if __name__ == '__main__':
    filename = 'pt23_hippo_lsp.wav'
    results = calculate_rms_window(filename)
