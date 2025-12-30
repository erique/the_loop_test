# Makefile for HippoPlayer test harness

VASM = /opt/amiga/bin/vasmm68k_mot
VASMFLAGS = -Fhunkexe -nosym
INCLUDES = -I/opt/amiga/m68k-amigaos/ndk-include/ -I.

TARGET = test_hippoplayer
SOURCES = test_hippoplayer.s
DEPS = kpl14.s mucro.i the_loop.mod

all: $(TARGET)

$(TARGET): $(SOURCES) $(DEPS)
	$(VASM) $(INCLUDES) $(VASMFLAGS) -o $(TARGET) $(SOURCES)

clean:
	rm -f $(TARGET)

rebuild: clean all

.PHONY: all clean rebuild
