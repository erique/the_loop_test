# Raw PAULA 4-Channel Capture

This feature captures each of the 4 PAULA channels separately, before they're mixed together into stereo output.

## Configuration Option

Add to your `.fs-uae` configuration file:

```
sound_paula_capture_channels_file = output_filename.pcm
```

Or use the command line:

```bash
./fs-uae/fs-uae --uae_sound_paula_capture_channels_file=output.pcm <config_file>
```

## Test Configuration

The file `record_pt23f_raw_channels.fs-uae` demonstrates how to use this feature.

### Running the Test

```bash
cd /Users/erik/src/the_loop_test
./record_pt23f_raw_channels.sh
```

Or directly:

```bash
cd /Users/erik/src/the_loop_test
./fs-uae/fs-uae record_pt23f_raw_channels.fs-uae
```

## Output Format

The captured `.pcm` file contains:
- **Format**: Raw PCM (no header)
- **Sample Format**: 16-bit signed little-endian (s16le)
- **Channels**: 4 (PAULA channels 0, 1, 2, 3)
- **Channel Layout**: Interleaved (CH0, CH1, CH2, CH3, CH0, CH1, CH2, CH3, ...)
- **Sample Rate**: 96000 Hz (matches the configured `audio_frequency`)
- **Byte Order**: Little-endian

### What's Captured

The capture happens **after** volume multiplication but **before**:
- Channel mixing (stereo or mono mix)
- Filtering
- Any final output processing

Each channel contains:
- **Channel 0**: Typically left front (Paula channel 0)
- **Channel 1**: Typically right front (Paula channel 1)
- **Channel 2**: Typically right rear (Paula channel 2)
- **Channel 3**: Typically left rear (Paula channel 3)

The Amiga's audio panning is typically:
- Channels 0 and 3 → Left speaker
- Channels 1 and 2 → Right speaker

## Converting to WAV

### Full 4-Channel WAV

To convert the raw 4-channel PCM to a standard WAV file:

```bash
ffmpeg -f s16le -ar 96000 -ac 4 -i pt23f_channels_raw.pcm pt23f_channels_raw.wav
```

### Extract Individual Channels

To split into 4 separate mono WAV files (one per PAULA channel):

```bash
ffmpeg -f s16le -ar 96000 -ac 4 -i pt23f_channels_raw.pcm \
  -filter_complex "channelsplit=channel_layout=quad[c0][c1][c2][c3]" \
  -map "[c0]" paula_ch0.wav \
  -map "[c1]" paula_ch1.wav \
  -map "[c2]" paula_ch2.wav \
  -map "[c3]" paula_ch3.wav
```

### Mix to Stereo with Amiga Panning

To create a stereo mix with proper Amiga panning (0+3→L, 1+2→R):

```bash
ffmpeg -f s16le -ar 96000 -ac 4 -i pt23f_channels_raw.pcm \
  -filter_complex "[0:a]channelsplit=channel_layout=quad[c0][c1][c2][c3]; \
                   [c0][c3]amix=inputs=2[left]; \
                   [c1][c2]amix=inputs=2[right]; \
                   [left][right]join=inputs=2:channel_layout=stereo[out]" \
  -map "[out]" pt23f_stereo_mix.wav
```

## Comparison with Other Capture Methods

### Normal FS-UAE Audio Recording
- Captures final stereo output at configured frequency (e.g., 96kHz)
- All 4 channels already mixed to stereo
- Includes filtering and processing
- WAV format with headers

### `sound_paula_capture_file` (Mixed Output)
- Captures mixed stereo output at configured frequency
- Samples from PAULA buffer before SDL
- Raw PCM format (2 channels)
- Less processing than normal recording

### `sound_paula_capture_channels_file` (Individual Channels) ⭐ **YOU ARE HERE**
- Captures all 4 PAULA channels **separately**
- After volume multiplication, before mixing
- Raw PCM format (4 channels interleaved)
- Allows custom mixing, panning, and analysis
- **This is the "truly raw channels" option**

## Use Cases

1. **Custom mixing** - Create your own stereo mix with different panning
2. **Channel analysis** - Analyze what each tracker channel is playing
3. **Debugging** - See exactly what each PAULA channel outputs
4. **Music extraction** - Separate bass, melody, drums, etc. by channel
5. **Research** - Study how different replayers use the 4 channels
6. **Remixing** - Create new mixes from original channel data

## Technical Details

- Channels are captured at the output sample rate (96kHz), not at individual DMA rates
- Volume is already applied (0-64 scale multiplied by sample value)
- Sample interpolation (sinc, anti-aliasing, etc.) is already applied per channel
- Each sample is the final 16-bit value for that channel before mixing
