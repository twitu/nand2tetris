@17
D=A
@SP
A=M
M=D
@SP
M=M+1
@17
D=A
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
@RETURNHERE0
D=A
@R13
M=D
@EQUAL
0;JMP
(RETURNHERE0)
@SP
M=M+1
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
@16
D=A
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
@RETURNHERE1
D=A
@R13
M=D
@EQUAL
0;JMP
(RETURNHERE1)
@SP
M=M+1
@16
D=A
@SP
A=M
M=D
@SP
M=M+1
@17
D=A
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
@RETURNHERE2
D=A
@R13
M=D
@EQUAL
0;JMP
(RETURNHERE2)
@SP
M=M+1
@892
D=A
@SP
A=M
M=D
@SP
M=M+1
@891
D=A
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
@RETURNHERE3
D=A
@R13
M=D
@LESS
0;JMP
(RETURNHERE3)
@SP
M=M+1
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
@892
D=A
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
@RETURNHERE4
D=A
@R13
M=D
@LESS
0;JMP
(RETURNHERE4)
@SP
M=M+1
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
@891
D=A
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
@RETURNHERE5
D=A
@R13
M=D
@LESS
0;JMP
(RETURNHERE5)
@SP
M=M+1
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1
@32766
D=A
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
@RETURNHERE6
D=A
@R13
M=D
@GREATER
0;JMP
(RETURNHERE6)
@SP
M=M+1
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
@32767
D=A
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
@RETURNHERE7
D=A
@R13
M=D
@GREATER
0;JMP
(RETURNHERE7)
@SP
M=M+1
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
@32766
D=A
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
@RETURNHERE8
D=A
@R13
M=D
@GREATER
0;JMP
(RETURNHERE8)
@SP
M=M+1
@57
D=A
@SP
A=M
M=D
@SP
M=M+1
@31
D=A
@SP
A=M
M=D
@SP
M=M+1
@53
D=A
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
@112
D=A
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
@SP
A=M-1
M=-M
@SP
AM=M-1
D=M
@SP
AM=M-1
M=M&D
@SP
M=M+1
@82
D=A
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
M=M|D
@SP
M=M+1
@SP
A=M-1
M=!M
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