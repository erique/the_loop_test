#!/bin/sh
# HippoPlayer raw PAULA 4-channel capture - captures individual channels separately

echo "Starting HippoPlayer raw 4-channel PAULA capture test..."
echo "Raw 4-channel samples will be written to: hippoplayer_channels_raw.pcm"
echo ""

timeout 120s ./fs-uae/fs-uae --stdout \
    --hard_drive_0=test_hippoplayer \
    --hard_drive_0_label=HIPPOPLAYER \
    --uae_sound_paula_capture_channels_file=hippoplayer_channels_raw.pcm \
    record_raw_channels.fs-uae
./strip_leading_silence.py hippoplayer_channels_raw.pcm hippoplayer_channels_trimmed.pcm
rm hippoplayer_channels_raw.pcm
mv hippoplayer_channels_trimmed.pcm hippoplayer_channels_raw.pcm

echo ""
echo "Test complete!"
echo ""
echo "To analyze the raw 4-channel PCM file, you can use ffmpeg to convert it:"
echo ""
echo "Example (96000Hz, 4 channels interleaved):"
echo "  ffmpeg -f s16le -ar 96000 -ac 4 -i hippoplayer_channels_raw.pcm hippoplayer_channels_raw.wav"
echo ""
echo "To extract individual channels:"
echo "  ffmpeg -f s16le -ar 96000 -ac 4 -i hippoplayer_channels_raw.pcm -filter_complex \"channelsplit=channel_layout=quad[c0][c1][c2][c3]\" -map \"[c0]\" hippoplayer_ch0.wav -map \"[c1]\" hippoplayer_ch1.wav -map \"[c2]\" hippoplayer_ch2.wav -map \"[c3]\" hippoplayer_ch3.wav"
echo ""
