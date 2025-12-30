#!/bin/sh
# PT2.3F recording - launch FS-UAE with BlackHole audio output

echo "Starting PT2.3F test..."
echo "Audio will be routed to BlackHole 16ch"
echo ""

../fs-uae/fs-uae --stdout record_pt23f.fs-uae

echo ""
echo "Test complete!"
