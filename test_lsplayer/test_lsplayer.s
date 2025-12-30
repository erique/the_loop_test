; Test harness for LSPlayer CIA with "The Loop" module
; Plays converted LSP module for 120 seconds using dos.library/Delay()

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

	; Initialize LSPlayer CIA driver
	; a0 = LSP music data (any memory)
	; a1 = LSP sound bank (chip memory)
	; a2 = VBR (0 for 68000)
	; d0 = 0 for PAL, 1 for NTSC
	lea	lsp_music,a0
	lea	lsp_bank,a1
	suba.l	a2,a2			; VBR = 0 for 68000
	moveq	#0,d0			; PAL
	bsr.w	LSP_MusicDriver_CIA_Start

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
	; Stop LSPlayer CIA driver
	bsr.w	LSP_MusicDriver_CIA_Stop

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

custom	=	$dff000

; Include LSPlayer (standard player first, then CIA wrapper)
	include	"LightSpeedPlayer.asm"
	include	"LightSpeedPlayer_cia.asm"

; LSP Music data (can be in any memory)
	section lspmusic,data
lsp_music:
	incbin	"the_loop.lsmusic"

; LSP Sound bank (must be in chip memory)
	section lspbank,data_c
lsp_bank:
	incbin	"the_loop.lsbank"
