# Makefile for PT2.3F test harness

VASM = /opt/amiga/bin/vasmm68k_mot
VASMFLAGS = -Fhunkexe -nosym

TARGET = test_pt23f
SOURCES = test_pt23f.s
DEPS = PT2.3F_replay_vblank.s pt23f_replayer_only.s the_loop.mod

all: $(TARGET)

$(TARGET): $(SOURCES) $(DEPS)
	$(VASM) $(VASMFLAGS) -o $(TARGET) $(SOURCES)

clean:
	rm -f $(TARGET)

rebuild: clean all

.PHONY: all clean rebuild
