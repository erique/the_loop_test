# Makefile for LSPlayer test harness

VASM = /opt/amiga/bin/vasmm68k_mot
VASMFLAGS = -Fhunkexe -nosym

TARGET = test_lsplayer
SOURCES = test_lsplayer.s
DEPS = LightSpeedPlayer.asm LightSpeedPlayer_cia.asm the_loop.lsmusic the_loop.lsbank

all: $(TARGET)

$(TARGET): $(SOURCES) $(DEPS)
	$(VASM) $(VASMFLAGS) -o $(TARGET) $(SOURCES)

clean:
	rm -f $(TARGET)

rebuild: clean all

.PHONY: all clean rebuild
