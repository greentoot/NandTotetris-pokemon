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


//code de Test.vm
(Main.test)

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

// push constant 10
@10
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop local 0
@LCL
D=M
@0
D=D+A
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D

// push constant 20
@20
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop local 1
@LCL
D=M
@1
D=D+A
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
// push local 0
@LCL
D=M
@0
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
// push local 1
@LCL
D=M
@1
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
AM=M-1
D=M
A=A-1
M=M+D


// push constant 30
@30
D=A
@SP
A=M
M=D
@SP
M=M+1
// sub
@SP
AM=M-1
D=M
A=A-1
M=M-D

// push constant 0
@0
D=A
@SP
A=M
M=D
@SP
M=M+1
