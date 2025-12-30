# Audio Recording Instructions for The Loop Module Tests

## Overview
This directory contains three test executables, each using a different ProTracker replayer to play "The Loop" module for exactly 120 seconds. The goal is to record the audio output and compare them to identify playback differences.

## Test Executables

1. **test_pt23f/test_pt23f** - ProTracker 2.3F CIA replayer
2. **test_hippoplayer/test_hippoplayer** - HippoPlayer KPlayer v33 replayer (mode 1)
3. **test_lsplayer/test_lsplayer** - LSPlayer (Light Speed Player) with converted LSP format

All tests play for exactly **120 seconds** (6000 frames @ 50fps) using vblank timing.

## Recording Setup with BlackHole + Audacity

### Prerequisites
- **BlackHole 16ch** - Virtual audio device (already installed)
- **Audacity** - Audio recording software
- **FS-UAE** - Amiga emulator

### Step 1: Configure FS-UAE Audio Output

The FS-UAE configs are already set to output audio to BlackHole:
- `record_pt23f.fs-uae`
- `record_hippoplayer.fs-uae`
- `record_lsplayer.fs-uae`

Each config includes:
```
audio_output_device = BlackHole 16ch
```

### Step 2: Set Up Audacity

1. **Open Audacity**
2. **Select Recording Device:**
   - Click the microphone dropdown in the toolbar
   - Select **"BlackHole 16ch"** as the input device
3. **Set Project Rate:**
   - At the bottom left, set project rate to **44100 Hz**
4. **Prepare to Record:**
   - Click the red **Record** button (but don't start yet)

### Step 3: Record Each Test

For each test (PT2.3F, HippoPlayer, LSPlayer):

1. **Start Audacity Recording:**
   - Click the red **Record** button in Audacity

2. **Launch FS-UAE Test:**
   ```bash
   ../fs-uae/fs-uae --stdout record_pt23f.fs-uae
   # or
   ../fs-uae/fs-uae --stdout record_hippoplayer.fs-uae
   # or
   ../fs-uae/fs-uae --stdout record_lsplayer.fs-uae
   ```

3. **Wait for Test to Complete:**
   - The startup-sequence will automatically run the test
   - Music plays for exactly 120 seconds
   - Test exits automatically

4. **Stop Audacity Recording:**
   - Click the **Stop** button (black square) in Audacity

5. **Export to WAV:**
   - File → Export → Export Audio...
   - Format: **WAV (Microsoft) signed 16-bit PCM**
   - Filename:
     - `pt23f_recording.wav`
     - `hippoplayer_recording.wav`
     - `lsplayer_recording.wav`
   - Click **Save**

6. **Clear Audacity for Next Recording:**
   - File → Close
   - Don't save the project
   - Repeat for the next test

### Alternative: Manual Startup (if startup-sequence doesn't work)

If the automatic startup-sequence doesn't run:

1. In FS-UAE, open Shell/CLI
2. Type: `DH0:test_pt23f` (or test_hippoplayer, test_lsplayer)
3. Press Enter
4. Music will play for 120 seconds

## Expected Output Files

After recording all three tests:
- `pt23f_recording.wav` - PT2.3F playback (120 seconds)
- `hippoplayer_recording.wav` - HippoPlayer playback (120 seconds)
- `lsplayer_recording.wav` - LSPlayer playback (120 seconds)

## Audio Configuration

All recordings use:
- Sample rate: 44100 Hz
- Format: WAV signed 16-bit PCM, stereo
- Emulated system: A1200/020 with 2MB Chip + 8MB Fast RAM
- Duration: Exactly 120 seconds (6000 vblank frames)

## Analyzing the Recordings

### 1. Visual Comparison in Audacity
```bash
# Open all three files
audacity pt23f_recording.wav hippoplayer_recording.wav lsplayer_recording.wav
```

- Compare waveforms visually
- Look for differences in amplitude, timing, or effects
- Use Analyze → Plot Spectrum to compare frequency content

### 2. Command-line Analysis with SoX

If you have SoX installed:

```bash
# Compare duration
soxi pt23f_recording.wav hippoplayer_recording.wav lsplayer_recording.wav

# Generate spectrograms
sox pt23f_recording.wav -n spectrogram -o pt23f_spectrogram.png
sox hippoplayer_recording.wav -n spectrogram -o hippoplayer_spectrogram.png
sox lsplayer_recording.wav -n spectrogram -o lsplayer_spectrogram.png

# Compare audio stats
sox pt23f_recording.wav -n stats 2>&1 | grep "RMS\|Maximum"
sox hippoplayer_recording.wav -n stats 2>&1 | grep "RMS\|Maximum"
sox lsplayer_recording.wav -n stats 2>&1 | grep "RMS\|Maximum"
```

### 3. Python Analysis (librosa, scipy)

For detailed analysis:
- Load WAV files with `librosa` or `scipy.io.wavfile`
- Compute waveform differences
- Calculate RMS differences
- Perform cross-correlation
- Identify specific divergence points
- Generate difference plots

## Troubleshooting

**No audio in Audacity while recording:**
- Verify FS-UAE is outputting to BlackHole (check audio_output_device in config)
- Verify Audacity is recording from BlackHole 16ch
- Check that Audacity's recording meter shows levels during playback

**Can't hear the audio during recording:**
- This is normal - audio is routed to BlackHole, not your speakers
- To monitor audio, set up a Multi-Output Device in Audio MIDI Setup:
  1. Open Audio MIDI Setup
  2. Click + → Create Multi-Output Device
  3. Check both "BlackHole 16ch" and your speakers
  4. Use this Multi-Output Device in FS-UAE config instead

**Test doesn't start automatically:**
- Check that S/startup-sequence exists in test directory
- Verify file has Unix line endings (not Windows CRLF)
- Manually run from Shell: `DH0:test_<name>`

**Recording is shorter/longer than 120 seconds:**
- All tests are configured for exactly 6000 vblank frames
- If shorter: test may have crashed or been interrupted
- If longer: you may have started recording too early
- Trim in Audacity if needed

## Rebuilding Tests

If you need to modify the tests:

```bash
# Rebuild all tests
make

# Rebuild individual test
cd test_pt23f && make rebuild
cd test_hippoplayer && make rebuild
cd test_lsplayer && make rebuild
```

## Test Configuration Details

### PT2.3F
- Replayer: PT2.3F CIA timer version
- Timing: CIA interrupts for music, vblank counting for duration
- File: `test_pt23f/test_pt23f`

### HippoPlayer
- Replayer: KPlayer v33 (kpl14.s)
- Mode: 1 (CIAB timer B interrupt)
- Flags: 3 (tempo + fast ram)
- Timing: CIA interrupts for music, vblank counting for duration
- File: `test_hippoplayer/test_hippoplayer`

### LSPlayer
- Replayer: Light Speed Player CIA version
- Format: Module converted to LSP format (.lsmusic + .lsbank)
- Timing: CIA interrupts for music, vblank counting for duration
- File: `test_lsplayer/test_lsplayer`
