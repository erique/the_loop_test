# Raw PAULA Audio Capture

This feature allows you to capture the raw audio samples directly from the PAULA chip emulation, before they are resampled to the output frequency (typically 44.1kHz).

## Configuration Option

Add to your `.fs-uae` configuration file:

```
sound_paula_capture_file = output_filename.pcm
```

## Test Configuration

The file `record_pt23f_raw_paula.fs-uae` demonstrates how to use this feature.

### Running the Test

```bash
cd /Users/erik/src/the_loop_test
./record_pt23f_raw_paula.sh
```

Or directly:

```bash
cd /Users/erik/src/the_loop_test
./fs-uae/fs-uae record_pt23f_raw_paula.fs-uae
```

## Output Format

The captured `.pcm` file contains:
- **Format**: Raw PCM (no header)
- **Sample Format**: 16-bit signed little-endian (s16le)
- **Channels**: 2 (stereo, interleaved: left, right, left, right, ...)
- **Sample Rate**: The configured output frequency (96000 Hz in the test config)
- **Byte Order**: Little-endian (native system byte order on most platforms)

**Important Note**: The current implementation captures the mixed and interpolated output samples at the configured audio frequency (typically 44.1kHz), not the raw individual PAULA channel samples at their native periods. The PAULA emulation uses interpolation to generate samples at the output rate.

## Converting to WAV

To convert the raw PCM to a standard WAV file, use `ffmpeg` with the configured sample rate:

```bash
# For 96kHz output (as configured in record_pt23f_raw_paula.fs-uae)
ffmpeg -f s16le -ar 96000 -ac 2 -i pt23f_paula_raw.pcm pt23f_paula_raw.wav

# For other configured frequencies, adjust -ar accordingly
ffmpeg -f s16le -ar <your_audio_frequency> -ac 2 -i pt23f_paula_raw.pcm pt23f_paula_raw.wav
```

## Finding the Exact Sample Rate

The sample rate used for the capture is the configured `audio_frequency` setting in your `.fs-uae` configuration file. In the test configuration `record_pt23f_raw_paula.fs-uae`, this is set to 96000 Hz.

You can verify the frequency by checking:
1. The `audio_frequency` line in your `.fs-uae` config file
2. The FS-UAE log output which shows: `amiga_set_audio_frequency: <frequency>`

## Differences from Normal Recording

### Normal FS-UAE Audio Recording
- Uses the `audio_record` console command
- Captures audio **after** resampling to configured frequency
- Includes any mixing, filtering, and DSP processing
- Produces a standard WAV file

### Raw PAULA Capture (Current Implementation)
- Uses the `sound_paula_capture_file` config option
- Captures mixed stereo output at the configured frequency
- Samples are taken from the PAULA emulation buffer
- Does **not** include SDL processing/conversion
- Produces a raw PCM file (needs conversion)
- Sample rate matches the configured `audio_frequency` (typically 96kHz)

**Note**: Despite the name "raw PAULA", this currently captures the interpolated/mixed output at the configured audio frequency, not the individual channel samples at their native PAULA periods.

## Use Cases

1. **Analyzing exact replay frequencies** - See the actual sample rate used by the replayer
2. **Timing analysis** - Measure exact timing of audio events
3. **Comparing different resampling methods** - Capture raw data for offline processing
4. **Research and debugging** - Understand how PAULA generates audio
