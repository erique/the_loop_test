#!/bin/sh
# HippoPlayer recording - launch FS-UAE with BlackHole audio output

echo "Starting HippoPlayer test..."
echo "Audio will be routed to BlackHole 16ch"
echo ""

../fs-uae/fs-uae --stdout record_hippoplayer.fs-uae

echo ""
echo "Test complete!"
