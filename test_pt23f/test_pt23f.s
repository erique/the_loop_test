; Test harness for PT2.3F CIA replayer with "The Loop" module
; Plays module for 120 seconds using dos.library/Delay()

	section code,code

main:
	movem.l	d0-a6,-(sp)

	; Open dos.library
	move.l	4.w,a6
	lea	dosname(pc),a1
	moveq	#0,d0
	jsr	-552(a6)		; OpenLibrary
	move.l	d0,dosbase
	beq.w	exit_nodos

	; Install CIA interrupt and initialize module
	bsr.w	SetCIAInt
	bsr.w	mt_init
	st	mt_Enable		; Enable playback

	; Play for 120 seconds (120 iterations of 1 second each)
	move.w	#120,d7

playloop:
	; Delay for 1 second (50 ticks @ 50Hz)
	move.l	dosbase(pc),a6
	move.l	#50,d1
	jsr	-198(a6)		; Delay

	; Check for left mouse button (emergency exit)
	btst	#6,$bfe001
	beq.b	exitloop

	subq.w	#1,d7
	bne.b	playloop

exitloop:
	; Stop music and remove CIA interrupt
	bsr.w	mt_end
	bsr.w	ResetCIAInt

	; Close dos.library
	move.l	4.w,a6
	move.l	dosbase(pc),a1
	jsr	-414(a6)		; CloseLibrary

exit_nodos:
	movem.l	(sp)+,d0-a6
	rts

dosname:
	dc.b	"dos.library",0
	even

dosbase:
	dc.l	0

; Include PT2.3F CIA replayer (skip lines 1-67 which contain test code)
	include "pt23f_replayer_only.s"

; Module data
	section music,data_c
	cnop 0,4
mt_data:
	incbin	"the_loop.mod"
