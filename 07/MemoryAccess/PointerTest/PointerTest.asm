@3030
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M
@3
M=D
@3040
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M
@4
M=D
@32
D=A
@SP
A=M
M=D
@SP
M=M+1
@THIS
D=M
@2
D=D+A
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
@46
D=A
@SP
A=M
M=D
@SP
M=M+1
@THAT
D=M
@6
D=D+A
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
@3
D=M
@SP
A=M
M=D
@SP
M=M+1
@4
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M
@SP
AM=M-1
M=M+D
@SP
M=M+1
@THIS
D=M
@2
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M
@SP
AM=M-1
M=M-D
@SP
M=M+1
@THAT
D=M
@6
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M
@SP
AM=M-1
M=M+D
@SP
M=M+1
(END)
@END
0;JMP
(EQUAL)
@SP
A=M
D=M
@FALSE
D;JNE
@SP
A=M
M=-1
@R13
A=M
0;JMP
(GREATER)
@SP
A=M
D=M
@FALSE
D;JLE
@SP
A=M
M=-1
@R13
A=M
0;JMP
(LESS)
@SP
A=M
D=M
@FALSE
D;JGE
@SP
A=M
M=-1
@R13
A=M
0;JMP
(FALSE)
@SP
A=M
M=0
@R13
A=M
0;JMP
