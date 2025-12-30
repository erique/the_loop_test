# Master Makefile for all replayer tests

SUBDIRS = test_pt23f test_hippoplayer test_lsplayer

all:
	@for dir in $(SUBDIRS); do \
		echo "Building $$dir..."; \
		$(MAKE) -C $$dir; \
	done

clean:
	@for dir in $(SUBDIRS); do \
		echo "Cleaning $$dir..."; \
		$(MAKE) -C $$dir clean; \
	done

rebuild:
	@for dir in $(SUBDIRS); do \
		echo "Rebuilding $$dir..."; \
		$(MAKE) -C $$dir rebuild; \
	done

.PHONY: all clean rebuild
