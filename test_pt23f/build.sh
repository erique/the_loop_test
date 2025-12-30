#!/bin/bash
# Build script for PT2.3F test harness

echo "Building PT2.3F test harness..."
/opt/amiga/bin/vasmm68k_mot -Fhunkexe -o test_pt23f -nosym test_pt23f.s
if [ $? -eq 0 ]; then
    echo "Build successful: test_pt23f"
    ls -lh test_pt23f
else
    echo "Build failed!"
    exit 1
fi
