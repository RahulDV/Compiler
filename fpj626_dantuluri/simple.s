	.data
newline:	.asciiz "\n"
	.text
	.globl main
main:
	li $fp, 0x7ffffffc
B1:
	#readint       => 0
	li $v0, 5
	syscall
	add $t0, $v0, $zero
	sw $t0, -4($fp)
	#mov 0     => r_X
	lw $t0, -4($fp)
	sw $t0, 0($fp)
	#movi     2 => 1
	li $t0, 2
	sw $t0, -8($fp)
	#mul 1 r_X   => 2
	lw $t0, -8($fp)
	lw $t1, 0($fp)
	mulou $t2, $t0, $t1
	sw $t2, -12($fp)
	#writeint 2     =>  
	li $v0, 1
	lw $t1, -12($fp)
	add $a0, $t1, $zero
	syscall
	li $v0, 4
	la $a0, newline
	syscall
	#exit       =>  
	li $v0, 10
	syscall
