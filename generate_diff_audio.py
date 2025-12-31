#!/usr/bin/env python3
"""
Generate difference audio files to hear the differences between replayers.
"""

import wave
import struct
import sys

def load_wav(filename):
    """Load WAV file."""
    with wave.open(filename, 'rb') as wav:
        params = wav.getparams()
        frames = wav.readframes(params.nframes)
        samples = struct.unpack(f'{params.nframes * params.nchannels}h', frames)
        return list(samples), params

def save_wav(filename, samples, params):
    """Save samples to WAV file."""
    with wave.open(filename, 'wb') as wav:
        wav.setparams(params)
        packed = struct.pack(f'{len(samples)}h', *samples)
        wav.writeframes(packed)

def create_difference(samples1, samples2):
    """Create difference signal (amplified for audibility)."""
    min_len = min(len(samples1), len(samples2))
    diff = []

    for i in range(min_len):
        # Calculate difference and amplify by 10x for audibility
        d = (samples1[i] - samples2[i]) * 10

        # Clamp to 16-bit range
        d = max(-32768, min(32767, d))
        diff.append(d)

    return diff

if __name__ == '__main__':
    print("Loading recordings...")
    pt23f, params1 = load_wav('pt23f_recording.wav')
    hippo, params2 = load_wav('hippoplayer_recording.wav')
    lsp, params3 = load_wav('lsplayer_recording.wav')

    print(f"  PT2.3F:      {len(pt23f):,} samples")
    print(f"  HippoPlayer: {len(hippo):,} samples")
    print(f"  LSPlayer:    {len(lsp):,} samples")
    print()

    print("Generating difference files...")

    # PT2.3F vs HippoPlayer
    print("  pt23f_vs_hippo_diff.wav...")
    diff = create_difference(pt23f, hippo)
    save_wav('pt23f_vs_hippo_diff.wav', diff, params1)

    # PT2.3F vs LSPlayer
    print("  pt23f_vs_lsp_diff.wav...")
    diff = create_difference(pt23f, lsp)
    save_wav('pt23f_vs_lsp_diff.wav', diff, params1)

    # HippoPlayer vs LSPlayer
    print("  hippo_vs_lsp_diff.wav...")
    diff = create_difference(hippo, lsp)
    save_wav('hippo_vs_lsp_diff.wav', diff, params2)

    print()
    print("Done! Listen to the difference files to hear what's different.")
    print("The differences are amplified 10x for audibility.")
