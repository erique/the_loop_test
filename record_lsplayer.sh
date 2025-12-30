#!/bin/sh
# LSPlayer recording - launch FS-UAE with BlackHole audio output

echo "Starting LSPlayer test..."
echo "Audio will be routed to BlackHole 16ch"
echo ""

../fs-uae/fs-uae --stdout record_lsplayer.fs-uae

echo ""
echo "Test complete!"
