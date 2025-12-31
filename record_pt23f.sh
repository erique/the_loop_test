#!/bin/sh
# PT2.3F raw PAULA 4-channel capture - captures individual channels separately

echo "Starting PT2.3F raw 4-channel PAULA capture test..."
echo "Raw 4-channel samples will be written to: pt23f_channels_raw.pcm"
echo ""

timeout 120s ./fs-uae/fs-uae --stdout \
    --hard_drive_0=test_pt23f \
    --hard_drive_0_label=PT23F \
    --uae_sound_paula_capture_channels_file=pt23f_channels_raw.pcm \
    record_raw_channels.fs-uae
./strip_leading_silence.py pt23f_channels_raw.pcm pt23f_channels_trimmed.pcm
rm pt23f_channels_raw.pcm
mv pt23f_channels_trimmed.pcm pt23f_channels_raw.pcm

echo ""
echo "Test complete!"
echo ""
echo "To analyze the raw 4-channel PCM file, you can use ffmpeg to convert it:"
echo ""
echo "Example (96000Hz, 4 channels interleaved):"
echo "  ffmpeg -f s16le -ar 96000 -ac 4 -i pt23f_channels_raw.pcm pt23f_channels_raw.wav"
echo ""
echo "To extract individual channels:"
echo "  ffmpeg -f s16le -ar 96000 -ac 4 -i pt23f_channels_raw.pcm -filter_complex \"channelsplit=channel_layout=quad[c0][c1][c2][c3]\" -map \"[c0]\" pt23f_ch0.wav -map \"[c1]\" pt23f_ch1.wav -map \"[c2]\" pt23f_ch2.wav -map \"[c3]\" pt23f_ch3.wav"
echo ""
