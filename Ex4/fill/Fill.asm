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

// pseudo:
// while true (inf loop):
// temp = keyboard input
// if temp == 0: write "0" in every pixel in screen
// else: write "1" in every pixel in screen



(LOOP)
@KBD
D=M
@WHITE
D;JEQ    // if D == 0
@BLACK
D;JNE // if D != 0

@LOOP
0;JMP

//#########################################
(WHITE)
@SCREEN
D=A
@addresswhite
M=D // address = screen loc

@stopwhite
M=0

(WHITESCREENLOOP)
@stopwhite
D=M
@8192
D=D-A // D = stop-8192
@STOPWHITE
D;JEQ  // if stop == 8192: goto STOPWHITE

@addresswhite
A=M
M=0

@1
D=A
@addresswhite
M=D+M

@stopwhite
M = M + 1

@WHITESCREENLOOP
0;JMP

(STOPWHITE)
@LOOP
0;JMP



//#########################################
(BLACK)
@SCREEN
D=A
@address
M=D // address = screen loc

@stop
M=0

(SCREENLOOP)
@stop
D=M
@8192
D=D-A // D = stop-8192
@STOP
D;JEQ  // if stop == 8192: goto STOP

@address
A=M
M=-1

@1
D=A
@address
M=D+M

@stop
M = M + 1

@SCREENLOOP
0;JMP

(STOP)
@LOOP
0;JMP

