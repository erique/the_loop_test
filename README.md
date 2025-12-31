# ProTracker Replayer Comparison: "The Loop" Module

Comparing three ProTracker replayers (PT2.3F, HippoPlayer, LSPlayer) using high-fidelity raw 4-channel PAULA capture to identify playback differences in "The Loop" module.

## Overview

This project captures raw audio directly from the emulated PAULA chip (before stereo mixing) to enable precise, per-channel comparison of ProTracker replayers. Results show significant differences between replayers, particularly on Channel 1.

## Methodology

### Recording Setup

- **Emulator**: Custom FS-UAE with raw PAULA 4-channel capture support
  - Repository: https://github.com/erique/fs-uae
  - Branch: `paula-dump` (with `uae_sound_paula_capture_channels_file` feature)
- **Configuration**: Amiga 1200/020, 2MB Chip + 8MB Fast RAM
- **Sample Rate**: 96000 Hz
- **Format**: Raw PCM, 16-bit signed little-endian, 4 channels interleaved
- **Duration**: 120 seconds per replayer

### Capture Format

Raw PAULA output captures all 4 hardware channels separately **before** stereo mixing:
- **Channel 0**: Left front (Paula channel 0)
- **Channel 1**: Right front (Paula channel 1)
- **Channel 2**: Right rear (Paula channel 2)
- **Channel 3**: Left rear (Paula channel 3)

Standard Amiga panning: Ch0+Ch3 → Left, Ch1+Ch2 → Right

### Workflow

1. **Build test harnesses** for each replayer
2. **Record raw 4-channel PAULA output** using automated scripts
3. **Strip leading silence** automatically with `strip_leading_silence.py`
4. **Analyze per-channel differences** using NumPy-based analysis tools
5. **Generate 4-channel diff files** to visualize/hear differences

## Replayers Tested

### 1. ProTracker 2.3F (PT2.3F)
- **Source**: https://github.com/8bitbubsy/pt23f
- **Timing**: CIA timer interrupts
- **Directory**: `test_pt23f/`

### 2. HippoPlayer KPlayer v33
- **Source**: https://github.com/koobo/HippoPlayer
- **Replayer**: kpl14.s (ProTracker replayer)
- **Mode**: 1 (CIAB timer B), Flags: 3 (tempo + fast RAM)
- **Directory**: `test_hippoplayer/`

### 3. LSPlayer (Light Speed Player)
- **Source**: https://github.com/arnaud-carre/LSPlayer
- **Timing**: CIA timer
- **Format**: Module converted from .mod to LSP format
- **Directory**: `test_lsplayer/`

## Recording Scripts

All scripts use the shared `record_raw_channels.fs-uae` configuration and pass replayer-specific settings via command line:

- `./record_pt23f.sh` - Record PT2.3F → `pt23f_channels_raw.pcm`
- `./record_hippoplayer.sh` - Record HippoPlayer → `hippoplayer_channels_raw.pcm`
- `./record_lsplayer.sh` - Record LSPlayer → `lsplayer_channels_raw.pcm`
- `./record_all.sh` - Record all three sequentially

Each script automatically:
1. Runs FS-UAE with 120-second timeout
2. Captures raw 4-channel PAULA output at 96kHz
3. Strips leading silence
4. Outputs trimmed PCM file

## Analysis Tools

### analyze_recordings.py

NumPy-based analysis providing:
- **Overall correlation** between replayer pairs (1.0 = identical, 0.0 = unrelated)
- **Per-channel correlation** for each of the 4 PAULA channels
- **RMS and amplitude statistics** per channel
- **Difference metrics** (mean, median, std, max)
- **Divergence detection** (first frame where recordings differ)

Requires: `./venv/bin/python` with NumPy installed

```bash
./analyze_recordings.py
```

### generate_channel_diffs.py

Generates 4-channel difference files for each comparison:
- `pt2.3f_vs_hippoplayer_diff.pcm`
- `pt2.3f_vs_lsplayer_diff.pcm`
- `hippoplayer_vs_lsplayer_diff.pcm`

Each diff file contains all 4 channels (Ch0-Ch3 differences) in interleaved format.

```bash
./venv/bin/python generate_channel_diffs.py
```

### analyze_determinism.py

Tests FS-UAE determinism by comparing multiple recordings of the same replayer:

```bash
./analyze_determinism.py
```

Compares `hippoplayer_channels_raw_take1.pcm`, `take2.pcm`, and `take3.pcm` to measure run-to-run variation.

## Results

### Key Findings

**Overall Correlation (1.0 = identical, 0.0 = unrelated):**
- PT2.3F vs HippoPlayer: **0.889** (quite similar)
- PT2.3F vs LSPlayer: **0.635** (moderately different)
- HippoPlayer vs LSPlayer: **0.651** (moderately different)

**Per-Channel Correlation:**
- **Channel 3** shows highest similarity between PT2.3F and HippoPlayer (0.964)
- **Channel 1** shows largest differences across all comparisons (0.268-0.734)
- **Channel 0** moderately consistent (0.778-0.924)
- **Channel 2** varies significantly (0.470-0.807)

### Statistics Summary

| Replayer    | Frames      | Duration  | Ch0 RMS | Ch1 RMS | Ch2 RMS | Ch3 RMS |
|-------------|-------------|-----------|---------|---------|---------|---------|
| PT2.3F      | 11,233,303  | 117.01s   | 3817.92 | 2289.46 | 2189.10 | 3014.76 |
| HippoPlayer | 11,248,461  | 117.17s   | 3823.45 | 2286.98 | 2182.44 | 3011.91 |
| LSPlayer    | 11,280,947  | 117.51s   | 3838.09 | 2288.80 | 2187.34 | 3015.13 |

All channels max out at ±8192 (expected for PAULA's 8-bit output scaled to 16-bit).

### Interpretation

The per-channel analysis reveals:
1. **PT2.3F and HippoPlayer** are quite similar overall (0.889), with Channel 3 nearly identical (0.964)
2. **LSPlayer differs significantly** from both, especially on Channel 1
3. **Channel 1 is the primary source of variation** across all replayers
4. Differences are substantial (87-98% of samples differ beyond threshold)

### FS-UAE Non-Determinism

Testing revealed that **FS-UAE is not deterministic** - repeated recordings of the same replayer produce different results:

**Determinism Test Results** (3 identical runs of HippoPlayer):
- **Correlation between takes**: 0.936-0.938 (not 1.0)
- **Sample differences**: 25-30% of samples differ between runs
- **Recording lengths vary**: 116.05s, 117.11s, 117.17s
- **First differences**: Frame 4-30 (within first millisecond)

**Per-channel non-determinism:**
- **Channel 1**: Most variable (0.852-0.870 correlation)
- **Channel 3**: Most stable (0.981-0.986 correlation)
- **Channel 0 & 2**: Moderate variation (0.907-0.950)

**Implications:**
1. The replayer differences measured (0.635-0.889) are **much larger** than the ~6% non-determinism noise
2. Comparison results are **still valid** - replayer differences dominate over run-to-run variation
3. Channel 1's high variability may be partially due to FS-UAE timing sensitivity
4. For highest precision, multiple takes should be averaged

**Analysis tool**: `./analyze_determinism.py` compares multiple recordings of the same replayer

## Converting PCM Files

### To WAV (4-channel)
```bash
ffmpeg -f s16le -ar 96000 -ac 4 -i pt23f_channels_raw.pcm pt23f_channels_raw.wav
```

### Extract Individual Channels
```bash
ffmpeg -f s16le -ar 96000 -ac 4 -i pt23f_channels_raw.pcm \
  -filter_complex "channelsplit=channel_layout=quad[c0][c1][c2][c3]" \
  -map "[c0]" pt23f_ch0.wav -map "[c1]" pt23f_ch1.wav \
  -map "[c2]" pt23f_ch2.wav -map "[c3]" pt23f_ch3.wav
```

### Mix to Stereo (Amiga panning: Ch0+Ch3→L, Ch1+Ch2→R)
```bash
ffmpeg -f s16le -ar 96000 -ac 4 -i pt23f_channels_raw.pcm \
  -filter_complex "[0:a]channelsplit=channel_layout=quad[c0][c1][c2][c3]; \
                   [c0][c3]amix=inputs=2[left]; \
                   [c1][c2]amix=inputs=2[right]; \
                   [left][right]join=inputs=2:channel_layout=stereo[out]" \
  -map "[out]" pt23f_stereo.wav
```

## Reproducing the Tests

### Prerequisites

- **VASM**: Motorola 68k assembler at `/opt/amiga/bin/vasmm68k_mot`
- **Custom FS-UAE**: With raw PAULA capture support (see above)
- **Python 3** with venv and NumPy

### Setup

1. **Build test harnesses:**
   ```bash
   make rebuild
   ```

2. **Initialize Python venv:**
   ```bash
   python3 -m venv venv
   ./venv/bin/pip install numpy
   ```

3. **Record all replayers:**
   ```bash
   ./record_all.sh
   ```

4. **Analyze recordings:**
   ```bash
   ./analyze_recordings.py
   ./venv/bin/python generate_channel_diffs.py
   ```

## Project Structure

```
the_loop_test/
├── README.md                           # This file
├── Makefile                            # Build all test harnesses
│
├── the_loop.mod                        # Original ProTracker module
│
├── test_pt23f/                         # PT2.3F test harness
├── test_hippoplayer/                   # HippoPlayer test harness
├── test_lsplayer/                      # LSPlayer test harness
│
├── record_raw_channels.fs-uae          # Shared FS-UAE config (96kHz, 4ch capture)
├── record_pt23f.sh                     # Record PT2.3F
├── record_hippoplayer.sh               # Record HippoPlayer
├── record_lsplayer.sh                  # Record LSPlayer
├── record_all.sh                       # Record all sequentially
│
├── pt23f_channels_raw.pcm              # PT2.3F recording (4ch, 96kHz)
├── hippoplayer_channels_raw.pcm        # HippoPlayer recording (4ch, 96kHz)
├── lsplayer_channels_raw.pcm           # LSPlayer recording (4ch, 96kHz)
│
├── pt2.3f_vs_hippoplayer_diff.pcm      # 4-channel difference file
├── pt2.3f_vs_lsplayer_diff.pcm         # 4-channel difference file
├── hippoplayer_vs_lsplayer_diff.pcm    # 4-channel difference file
│
├── analyze_recordings.py               # NumPy-based per-channel analysis
├── analyze_recordings_stdlib.py        # Stdlib-only version
├── generate_channel_diffs.py           # Generate 4-channel diff files
├── analyze_determinism.py              # Test FS-UAE determinism
├── strip_leading_silence.py            # Auto-trim leading silence
│
├── venv/                               # Python virtual environment (numpy)
│
├── RAW_PAULA_CHANNELS.md               # Documentation on 4-channel capture
├── RAW_PAULA_CAPTURE.md                # Documentation on PAULA capture
└── DATA_PACKAGE_README.txt             # Data package description
```

## References

- **PT2.3F**: https://github.com/8bitbubsy/pt23f
- **HippoPlayer**: https://github.com/koobo/HippoPlayer
- **LSPlayer**: https://github.com/arnaud-carre/LSPlayer
- **Custom FS-UAE**: https://github.com/erique/fs-uae (branch: `paula-dump`)

## License

Test harnesses and analysis scripts are provided as-is for research purposes.

Original replayer code retains original licenses (see respective repositories).

## Author

Erik Hemming

Generated: 2025-12-31
