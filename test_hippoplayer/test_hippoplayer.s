; Test harness for HippoPlayer (kpl14.s) with "The Loop" module
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

	; Allocate 2000 byte buffer for KPlayer variables
	move.l	#2000,d0
	move.l	#$10002,d1		; MEMF_CHIP | MEMF_CLEAR
	move.l	4.w,a6
	jsr	-198(a6)		; AllocMem
	tst.l	d0
	beq.w	exit_nomem
	move.l	d0,k_buffer

	; Initialize KPlayer
	; A0 = buffer, A1 = module, D0.b = start pos, D1.b = timing mode, D2.b = flags
	move.l	d0,a0			; Buffer
	lea	module_data,a1		; Module
	moveq	#0,d0			; Start position 0
	moveq	#1,d1			; Mode 1: tempo
	moveq	#3,d2			; Flags: tempo, fast ram
	bsr.w	k_init
	tst.l	d0
	bmi.w	exit_initfail

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
	; Stop music
	bsr.w	k_end

exit_initfail:
	; Free buffer
	move.l	k_buffer,a1
	move.l	#2000,d0
	move.l	4.w,a6
	jsr	-210(a6)		; FreeMem

	; Close dos.library
	move.l	4.w,a6
	move.l	dosbase(pc),a1
	jsr	-414(a6)		; CloseLibrary

exit_nodos:
exit_nomem:
	movem.l	(sp)+,d0-a6
	rts

dosname:
	dc.b	"dos.library",0
	even

dosbase:
	dc.l	0

k_buffer:
	dc.l	0

; Include KPlayer replayer
	include	"kpl14.s"

; Module data
	section data,data
module_data:
	incbin	"the_loop.mod"
