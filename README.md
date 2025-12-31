# ProTracker Replayer Comparison: "The Loop" Module

## Project Overview

This project tests and compares three different ProTracker replayers to verify reports that "The Loop" module has playback issues with various replayers (except HippoPlayer). By recording and analyzing the audio output from each replayer, we can identify and characterize the differences in playback.

### Goals

1. Create standalone test executables for multiple ProTracker replayers
2. Play "The Loop" module for exactly 120 seconds with each replayer
3. Record high-quality audio output from each test
4. Analyze and compare the recordings to identify playback differences

## Replayers Tested

### 1. ProTracker 2.3F (PT2.3F)
- **Source**: https://github.com/8bitbubsy/pt23f
- **Version**: PT2.3F CIA replayer
- **Timing**: CIA timer interrupts for music playback
- **Test executable**: `test_pt23f/test_pt23f`

### 2. HippoPlayer KPlayer v33
- **Source**: https://github.com/koobo/HippoPlayer
- **Replayer**: kpl14.s (ProTracker replayer)
- **Mode**: 1 (CIAB timer B interrupt)
- **Flags**: 3 (tempo + fast RAM)
- **Test executable**: `test_hippoplayer/test_hippoplayer`

### 3. LSPlayer (Light Speed Player)
- **Source**: https://github.com/arnaud-carre/LSPlayer
- **Version**: CIA timer version
- **Format**: Module converted from .mod to LSP format (.lsmusic + .lsbank)
- **Test executable**: `test_lsplayer/test_lsplayer`

## Test Harness Architecture

### Design Decisions

All test harnesses share the same architecture:

1. **Timing Method**: `dos.library/Delay()` instead of vblank counting
   - Simpler and more reliable
   - Delays for 1 second (50 ticks) in a loop, 120 iterations = 120 seconds
   - Allows emergency exit check every second via left mouse button

2. **Music Timing**: CIA timer interrupts
   - All replayers use CIA timers for music playback (not vblank)
   - This provides accurate ProTracker-compatible timing

3. **Auto-execution**: S/startup-sequence
   - Tests auto-start when directory is mounted as DH0: in FS-UAE
   - Uses Unix line endings (LF) - critical for AmigaDOS compatibility

### Test Harness Code Structure

Each test follows this pattern:

```asm
main:
    ; Open dos.library
    ; Initialize replayer
    ; Enable music playback

    ; Loop 120 times (1 second delay each iteration)
    move.w  #120,d7
playloop:
    ; Delay 1 second (50 ticks @ 50Hz PAL)
    move.l  dosbase(pc),a6
    move.l  #50,d1
    jsr     -198(a6)        ; Delay

    ; Check left mouse button for emergency exit
    btst    #6,$bfe001
    beq.b   exitloop

    subq.w  #1,d7
    bne.b   playloop

exitloop:
    ; Stop music
    ; Close dos.library
    rts
```

## Recording Setup

### Hardware/Software Configuration

- **Emulator**: FS-UAE (Amiga 1200/020 with 2MB Chip + 8MB Fast RAM)
- **Virtual Audio**: BlackHole 16ch (macOS virtual audio device)
- **Recording Software**: Audacity
- **Sample Rate**: 44100 Hz
- **Format**: WAV, 16-bit signed PCM, stereo

### FS-UAE Configuration

Each test has a corresponding `.fs-uae` config file with:

```ini
audio_frequency = 44100
audio_buffer_target_size = 2048
stereo_separation = 100
audio_output_device = BlackHole 16ch
floppy_drive_0_sounds = off
floppy_drive_1_sounds = off
```

### Recording Workflow

The recording was done manually:

1. Start Audacity recording from BlackHole 16ch @ 44100 Hz
2. Launch FS-UAE test (e.g., `./record_pt23f.sh`)
3. Music plays for 120 seconds and test exits automatically
4. Stop Audacity recording
5. Repeat for each replayer

All three tests were recorded sequentially in a single Audacity session, resulting in one combined WAV file: `pt23_hippo_lsp.wav` (391 seconds total).

## Audio Processing Pipeline

### Step 1: Split Combined Recording

The combined recording contained all three tests with silence gaps between them.

**Detection method**: Created `find_offsets.py` to analyze RMS levels in 1-second windows and detect silence/audio transitions.

**Detected segments**:
- PT2.3F: 9s → 130s (121 seconds)
- HippoPlayer: 137s → 258s (121 seconds)
- LSPlayer: 264s → 389s (125 seconds)

**Split command**:
```bash
ffmpeg -i pt23_hippo_lsp.wav -ss 9 -t 121 -c copy pt23f_recording.wav -y
ffmpeg -i pt23_hippo_lsp.wav -ss 137 -t 121 -c copy hippoplayer_recording.wav -y
ffmpeg -i pt23_hippo_lsp.wav -ss 264 -t 125 -c copy lsplayer_recording.wav -y
```

### Step 2: Remove Leading Silence

Initial split files still contained different amounts of leading silence due to startup timing variations.

**Detection method**: Created `find_exact_audio_start.py` to scan for the first non-zero sample in each file.

**Detected null frames** (all ~100ms of leading zeros):
- PT2.3F: 4,407 frames (99.932ms)
- HippoPlayer: 4,408 frames (99.955ms)
- LSPlayer: 4,406 frames (99.909ms)

**Trim commands**:
```bash
ffmpeg -i pt23f_recording.wav -af "atrim=start_sample=4407" pt23f_recording.wav -y
ffmpeg -i hippoplayer_recording.wav -af "atrim=start_sample=4408" hippoplayer_recording.wav -y
ffmpeg -i lsplayer_recording.wav -af "atrim=start_sample=4406" lsplayer_recording.wav -y
```

**Result**: All recordings now start immediately with audio at sample 1 (no leading null samples).

## Analysis Methods

### Statistical Analysis

Created two analysis scripts:

1. **`analyze_recordings.py`** - NumPy version
   - Fast array operations
   - Includes median and std deviation statistics
   - Requires: `numpy` (installed in venv)

2. **`analyze_recordings_stdlib.py`** - Standard library version
   - No dependencies beyond Python stdlib
   - Same core metrics (correlation, RMS, max amplitude, divergence detection)

**Metrics calculated**:
- RMS (Root Mean Square) per channel
- Maximum amplitude per channel
- Correlation coefficient between pairs
- Mean/median/max absolute difference
- Percentage of samples differing significantly (threshold > 100)
- First divergence point

### Difference Audio Generation

Created `generate_diff_audio.py` to generate audible difference files:

```python
# Calculate difference and amplify by 10x for audibility
diff = (sample1 - sample2) * 10
```

**Output files**:
- `pt23f_vs_hippo_diff.wav`
- `pt23f_vs_lsp_diff.wav`
- `hippo_vs_lsp_diff.wav`

These files allow you to *hear* the differences between replayers.

## Results

### Final Recording Statistics

| Replayer    | Frames      | Duration  | RMS (L/R)       | Max Amp (L/R) |
|-------------|-------------|-----------|-----------------|---------------|
| PT2.3F      | 5,305,715   | 120.31s   | 5895 / 3788     | 19660 / 18662 |
| HippoPlayer | 5,301,011   | 120.20s   | 5900 / 3786     | 19660 / 18662 |
| LSPlayer    | 5,504,349   | 124.82s   | 6012 / 3732     | 19660 / 18662 |

### Pairwise Comparison Results

#### PT2.3F vs HippoPlayer
- **Correlation**: 0.104 (very low, essentially no correlation)
- **Samples differing**: 99.56%
- **First divergence**: Frame 0 (0.000s)
- **Mean difference**: 4378
- **Median difference**: 2580

#### PT2.3F vs LSPlayer
- **Correlation**: -0.046 (negative, essentially no correlation)
- **Samples differing**: 99.75%
- **First divergence**: Frame 0 (0.000s)
- **Mean difference**: 4768
- **Median difference**: 2827

#### HippoPlayer vs LSPlayer
- **Correlation**: -0.260 (negative correlation)
- **Samples differing**: 99.33%
- **First divergence**: Frame 0 (0.000s)
- **Mean difference**: 5035
- **Median difference**: 2607

### Conclusions

**All three replayers produce significantly different audio output**:

1. Differences are present from the very first frame (0.000s)
2. Over 99% of samples differ significantly between each pair
3. Correlations are near zero or negative, indicating no meaningful similarity
4. The differences are not subtle - they are fundamental to the playback

This confirms the initial report that "The Loop" module plays differently across replayers. The differences are not minor timing variations but substantial differences in the actual audio waveform generated.

## Project Structure

```
the_loop_test/
├── README.md                           # This file
├── RECORDING_INSTRUCTIONS.md           # Manual recording workflow with Audacity
├── Makefile                            # Master build file for all tests
│
├── the_loop.mod                        # Original ProTracker module
│
├── test_pt23f/                         # PT2.3F test harness
│   ├── Makefile
│   ├── test_pt23f.s                    # Test harness source
│   ├── test_pt23f                      # Compiled executable
│   ├── pt23f_replayer_only.s           # PT2.3F replayer (extracted)
│   ├── PT2.3F_replay_cia.s             # Full PT2.3F CIA source
│   ├── PT2.3F_replay_vblank.s          # Full PT2.3F vblank source
│   ├── the_loop.mod                    # Module copy
│   └── S/startup-sequence              # Auto-start script
│
├── test_hippoplayer/                   # HippoPlayer test harness
│   ├── Makefile
│   ├── test_hippoplayer.s              # Test harness source
│   ├── test_hippoplayer                # Compiled executable
│   ├── kpl14.s                         # KPlayer v33 replayer
│   ├── mucro.i                         # Macro include file
│   ├── the_loop.mod                    # Module copy
│   └── S/startup-sequence              # Auto-start script
│
├── test_lsplayer/                      # LSPlayer test harness
│   ├── Makefile
│   ├── test_lsplayer.s                 # Test harness source
│   ├── test_lsplayer                   # Compiled executable
│   ├── LightSpeedPlayer.asm            # LSPlayer core
│   ├── LightSpeedPlayer_cia.asm        # CIA timer wrapper
│   ├── the_loop.lsmusic                # Converted LSP music data
│   ├── the_loop.lsbank                 # Converted LSP sample bank
│   ├── the_loop.mod                    # Original module
│   └── S/startup-sequence              # Auto-start script
│
├── record_pt23f.fs-uae                 # FS-UAE config for PT2.3F
├── record_hippoplayer.fs-uae           # FS-UAE config for HippoPlayer
├── record_lsplayer.fs-uae              # FS-UAE config for LSPlayer
│
├── record_pt23f.sh                     # Launch script for PT2.3F test
├── record_hippoplayer.sh               # Launch script for HippoPlayer test
├── record_lsplayer.sh                  # Launch script for LSPlayer test
├── record_all.sh                       # Launch all tests sequentially
│
├── pt23_hippo_lsp.wav                  # Combined recording (original)
├── pt23f_recording.wav                 # PT2.3F (split & trimmed)
├── hippoplayer_recording.wav           # HippoPlayer (split & trimmed)
├── lsplayer_recording.wav              # LSPlayer (split & trimmed)
│
├── pt23f_vs_hippo_diff.wav             # Difference audio (PT2.3F vs HippoPlayer)
├── pt23f_vs_lsp_diff.wav               # Difference audio (PT2.3F vs LSPlayer)
├── hippo_vs_lsp_diff.wav               # Difference audio (HippoPlayer vs LSPlayer)
│
├── analyze_recordings.py               # NumPy-based analysis script
├── analyze_recordings_stdlib.py        # Stdlib-only analysis script
├── generate_diff_audio.py              # Generate audible difference files
├── find_offsets.py                     # Find audio/silence transitions
├── detect_audio_start.py               # Detect first non-silent sample
├── find_exact_audio_start.py           # Find exact first non-zero frame
├── analyze_leading_silence.py          # Analyze leading null samples
│
├── venv/                               # Python virtual environment
│   └── (numpy, scipy installed)
│
├── HippoPlayer/                        # Cloned repository (not committed)
├── LSPlayer/                           # Cloned repository (not committed)
└── pt23f/                              # Cloned repository (not committed)
```

## Reproducing the Tests

### Prerequisites

- **Amiga cross-compiler**: VASM (Motorola syntax)
  - Path: `/opt/amiga/bin/vasmm68k_mot`
  - NDK includes: `/opt/amiga/m68k-amigaos/ndk-include/`
- **FS-UAE**: Amiga emulator with audio routing support
- **BlackHole 16ch**: macOS virtual audio device
- **Audacity**: Audio recording software
- **Python 3**: For analysis scripts

### Build All Tests

```bash
make rebuild
```

This builds all three test executables.

### Record Audio

#### Manual Method (Recommended)

1. Open Audacity, set input to "BlackHole 16ch", project rate 44100 Hz
2. Start recording in Audacity
3. Run test: `./record_pt23f.sh` (or hippoplayer, lsplayer)
4. Wait for test to complete (120 seconds)
5. Stop Audacity recording
6. Export as WAV (16-bit PCM)
7. Repeat for each replayer

See `RECORDING_INSTRUCTIONS.md` for detailed instructions.

### Analyze Recordings

#### Using NumPy (faster, more detailed):
```bash
source venv/bin/activate
python3 analyze_recordings.py
```

#### Using stdlib only (no dependencies):
```bash
python3 analyze_recordings_stdlib.py
```

#### Generate Difference Audio:
```bash
python3 generate_diff_audio.py
```

This creates `*_diff.wav` files with 10x amplified differences for audibility.

## Key Lessons Learned

### Technical Challenges

1. **Line Endings**: AmigaDOS requires Unix (LF) line endings, not Windows (CRLF)
   - Startup-sequence files must use LF or they fail silently

2. **HippoPlayer Configuration**: Initial attempts had no audio
   - Solution: Mode 1 (CIAB timer B), Flags 3 (tempo + fast RAM)

3. **Include File Paths**: HippoPlayer needed `lvo/exec_lib.i` not `exec/exec_lib.i`
   - LVO files contain library offsets, not function definitions

4. **Timing Method Evolution**:
   - Initially used vblank counting (complex, hardware-dependent)
   - Switched to `dos.library/Delay()` (simpler, more reliable)

5. **Audio Processing**:
   - ffmpeg's `silenceremove` filter is imprecise
   - Binary analysis to find exact first non-zero sample is more accurate

### Design Decisions

1. **CIA vs Vblank**: All replayers use CIA timer interrupts for music
   - More accurate to original ProTracker behavior
   - Vblank only used for 120-second duration in initial version

2. **120 Second Duration**: Consistent test length across all replayers
   - Long enough to capture repeating patterns
   - Short enough for practical recording/analysis

3. **LSP Conversion**: LSPlayer requires conversion from MOD to LSP format
   - Used official LSPConvert tool
   - Generates .lsmusic (music data) and .lsbank (sample bank)

## Future Work

### Potential Enhancements

1. **Spectral Analysis**: Generate spectrograms to visualize frequency differences
2. **Automated Recording**: Eliminate manual Audacity workflow
3. **Additional Replayers**: Test more replayers (e.g., EaglePlayer, UADE)
4. **Other Modules**: Test with different ProTracker modules
5. **Timing Analysis**: Measure exact tempo/timing variations
6. **Visual Waveform Comparison**: Generate overlaid waveform images

### Analysis Ideas

1. Identify specific pattern/sample playback differences
2. Correlate differences with module features (effects, tempo changes, etc.)
3. Create reference recordings from original Amiga hardware
4. Reverse-engineer the specific implementation differences causing variations

## References

- **PT2.3F**: https://github.com/8bitbubsy/pt23f
- **HippoPlayer**: https://github.com/koobo/HippoPlayer
- **LSPlayer**: https://github.com/arnaud-carre/LSPlayer
- **The Loop Module**: https://demozoo.org/ (original download source)
- **FS-UAE**: https://fs-uae.net/
- **BlackHole**: https://existential.audio/blackhole/

## License

Test harnesses and analysis scripts created for this project are provided as-is for research purposes.

Original replayer code retains its original licenses:
- PT2.3F: See pt23f repository
- HippoPlayer: See HippoPlayer repository
- LSPlayer: See LSPlayer repository

## Author

Erik Hemming (with assistance from Claude Code)

Generated: 2025-12-31
