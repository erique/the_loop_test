#!/bin/sh
# Record all three replayer tests sequentially

echo "========================================"
echo "Recording All Replayer Tests"
echo "========================================"
echo ""
echo "This will run three tests sequentially:"
echo "1. PT2.3F (120 seconds)"
echo "2. HippoPlayer (120 seconds)"
echo "3. LSPlayer (120 seconds)"
echo ""
echo "Audio routed to BlackHole 16ch"
echo "Record in Audacity before running each test"
echo ""
echo "Press Ctrl+C to cancel, or wait 5 seconds to start..."
sleep 5

echo ""
echo "========================================"
echo "Test 1/3: PT2.3F"
echo "========================================"
./record_pt23f.sh

echo ""
echo "========================================"
echo "Test 2/3: HippoPlayer"
echo "========================================"
./record_hippoplayer.sh

echo ""
echo "========================================"
echo "Test 3/3: LSPlayer"
echo "========================================"
./record_lsplayer.sh

echo ""
echo "========================================"
echo "All tests complete!"
echo "========================================"
