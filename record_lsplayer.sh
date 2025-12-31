#!/bin/sh
# LSPlayer raw PAULA 4-channel capture - captures individual channels separately

echo "Starting LSPlayer raw 4-channel PAULA capture test..."
echo "Raw 4-channel samples will be written to: lsplayer_channels_raw.pcm"
echo ""

timeout 120s ./fs-uae/fs-uae --stdout \
    --hard_drive_0=test_lsplayer \
    --hard_drive_0_label=LSPLAYER \
    --uae_sound_paula_capture_channels_file=lsplayer_channels_raw.pcm \
    record_raw_channels.fs-uae
./strip_leading_silence.py lsplayer_channels_raw.pcm lsplayer_channels_trimmed.pcm
rm lsplayer_channels_raw.pcm
mv lsplayer_channels_trimmed.pcm lsplayer_channels_raw.pcm

echo ""
echo "Test complete!"
echo ""
echo "To analyze the raw 4-channel PCM file, you can use ffmpeg to convert it:"
echo ""
echo "Example (96000Hz, 4 channels interleaved):"
echo "  ffmpeg -f s16le -ar 96000 -ac 4 -i lsplayer_channels_raw.pcm lsplayer_channels_raw.wav"
echo ""
echo "To extract individual channels:"
echo "  ffmpeg -f s16le -ar 96000 -ac 4 -i lsplayer_channels_raw.pcm -filter_complex \"channelsplit=channel_layout=quad[c0][c1][c2][c3]\" -map \"[c0]\" lsplayer_ch0.wav -map \"[c1]\" lsplayer_ch1.wav -map \"[c2]\" lsplayer_ch2.wav -map \"[c3]\" lsplayer_ch3.wav"
echo ""
