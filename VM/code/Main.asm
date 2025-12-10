// Bootstrap
    @256
    D=A
    @SP
    M=D
// call Sys.init 0
@RET_ADDR0          // push return address
D=A
@SP
A=M
M=D
@SP
M=M+1

@LCL            // push LCL
D=M
@SP
A=M
M=D
@SP
M=M+1

@ARG            // push ARG
D=M
@SP
A=M
M=D
@SP
M=M+1

@THIS           // push THIS
D=M
@SP
A=M
M=D
@SP
M=M+1

@THAT           // push THAT
D=M
@SP
A=M
M=D
@SP
M=M+1

@SP             // ARG = SP - nArgs - 5
D=M
@5
D=D-A
@ARG
M=D

@SP             // LCL = SP
D=M
@LCL
M=D

@Sys.init         // goto function
0;JMP

(RET_ADDR0)         // return address label


//code de Main.vm
(Main.main)
// push constant 0
@0
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 0
@0
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 0
@0
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 0
@0
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 0
@0
D=A
@SP
A=M
M=D
@SP
M=M+1
