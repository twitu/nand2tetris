// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

// Check keyboard for input
@8191
D=A
@POINTER
M=D
(CHECK)
	@KBD
	D=M
	@CHECKBLACK
	D;JNE
// Check if screen is already white
	@SCREEN
	D=M
// If white go back to check
	@CHECK
	D;JEQ
// Else make screen white
(LOOPWHITE)
	@POINTER
	D=M
	@REINIT
	D;JLT
	@SCREEN
	A=A+D
	M=0
	@POINTER
	M=D-1
	@LOOPWHITE
	0;JMP
(CHECKBLACK)
// Check if screen is already black
	@SCREEN
	D=M
	D=D+1
// If black go back to check
	@CHECK
	D;JEQ
// Else make screen black
(LOOPBLACK)
	@POINTER
	D=M
	@REINIT
	D;JLT
	@SCREEN
	A=A+D
	M=-1
	@POINTER
	M=D-1
	@LOOPBLACK
	0;JMP
(REINIT)
	@8191
	D=A
	@POINTER
	M=D
	@CHECK
	0;JMP