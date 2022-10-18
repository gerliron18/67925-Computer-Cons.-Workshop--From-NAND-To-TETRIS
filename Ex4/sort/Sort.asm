// This file is part of nand2tetris, as taught in The Hebrew University,
// and was written by Aviv Yaish, and is published under the Creative 
// Common Attribution-NonCommercial-ShareAlike 3.0 Unported License 
// https://creativecommons.org/licenses/by-nc-sa/3.0/

// An implementation of a sorting algorithm. 
// An array is given in R14 and R15, where R14 contains the start address of the 
// array, and R15 contains the length of the array. 
// You are not allowed to change R14, R15.
// The program should sort the array in-place and in descending order - 
// the largest number at the head of the array.
// You can assume that each array value x is between -16384 < x < 16384.
// You can assume that the address in R14 is at least >= 2048, and that 
// R14 + R15 <= 16383. 
// No other assumptions can be made about the length of the array.
// You can implement any sorting algorithm as long as its runtime complexity is 
// at most C*O(N^2), like bubble-sort. 

@R14
D = M
@address
M = D

@R15
D = M
@n
M = D

D = M - 1
@END //if n=1, jmp to END
D;JEQ 


@i
M = 0


(OUTERLOOP)
@i
D = M
@n
D = M - D
@END //if (n-i) < 0, jmp to END
D;JLE

@address
D = M
@curradd
M = D


(LOOP)
@address
D = M
@n
D = D + M
@curradd
D = D - M 
@i
D = D - M
D = D - 1
@OUTINCREMENT
D;JEQ //if address+n-curadd-i=0 goto OUTINCREMENT

@curradd
D = M
@nextadd
M = D + 1
@curradd
A = M
D = M
@nextadd
A = M
D = D - M

@SWAP //if list[curradd] < list[nextadd] then SWAP
D;JLT

@INCREMENT
0;JMP

(INCREMENT)
@curradd
M = M + 1

@LOOP //return to LOOP
0;JMP

(SWAP)
@curradd //temp = arr[curradd]
A = M
D = M
@temp
M = D

@nextadd //arr[curradd] = arr[nextadd]
A = M
D = M
@curradd
A = M
M = D

@temp //arr[nextadd] = temp
D = M
@nextadd
A = M
M = D

@INCREMENT
0;JMP


(OUTINCREMENT)
@i
M = M + 1
@OUTERLOOP
0;JMP


(END)
@END
0;JMP
