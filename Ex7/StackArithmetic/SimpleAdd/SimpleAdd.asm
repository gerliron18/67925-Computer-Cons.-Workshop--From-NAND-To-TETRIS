// SimpleAdd
// C_PUSH
@7
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH
@8
D=A
@SP
A=M
M=D
@SP
M=M+1
//add
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
M=D+M
@SP
M=M+1
