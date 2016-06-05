import IntermediateCodeGenerator
import sys

starting_block = IntermediateCodeGenerator.start()

dest_file = sys.argv[4]
file_object = open(dest_file, "w")
start = '\t.data\nnewline:\t.asciiz "\\n"\n\t.text\n\t.globl main\nmain:\n\tli $fp, 0x7ffffffc\n'
file_object.write(start)

regs_for_idents = {}
sp = 0


def populate_regs_for_idents():
    global regs_for_idents
    global sp
    for key, value in IntermediateCodeGenerator.get_ident_regs().items():
        regs_for_idents[value] = str(sp) + '($fp)'
        sp -= 4
    i = 0
    while i < IntermediateCodeGenerator.register_counter:
        regs_for_idents[i] = str(sp) + '($fp)'
        sp -= 4
        i += 1
    '''regs_for_idents[1] = str(sp)+'($fp)'
    sp -= 4
    regs_for_idents[2] = str(sp)+'($fp)'
    sp -= 4
    regs_for_idents[3] = str(sp)+'($fp)'
    sp -= 4'''


def generate_mips_code(block):
    instructions = block.get_instructions()
    string = block.get_block_name() + ':\n'
    for instruction in instructions:
        if instruction.get_label1() == ' ':
            iloc_instruction = '\t#{} {} {} {} => {}\n'.format(instruction.get_operation(),
                                                               instruction.get_source_reg1(),
                                                               instruction.get_source_reg2(),
                                                               instruction.get_immediate(),
                                                               instruction.get_destination_reg())
        else:
            iloc_instruction = '\t#{} {} {} -> {} {}\n'.format(instruction.get_operation(),
                                                               instruction.get_source_reg1(),
                                                               instruction.get_source_reg2(), instruction.get_label1(),
                                                               instruction.get_label2())
        operation = instruction.get_operation()
        mips = ''
        if operation == 'movi':
            mips = '\tli $t0, ' + instruction.get_immediate() + '\n\tsw $t0, ' + regs_for_idents[
                instruction.get_destination_reg()] + '\n'
        elif operation == 'mov':
            mips = '\tlw $t0, ' + regs_for_idents[instruction.get_source_reg1()] + '\n\tsw $t0, ' + regs_for_idents[
                instruction.get_destination_reg()] + '\n'
        elif operation == 'add':
            mips = '\tlw $t0, ' + regs_for_idents[instruction.get_source_reg1()] + '\n\tlw $t1, ' + regs_for_idents[
                instruction.get_source_reg2()] + '\n'
            mips = mips + '\taddu $t2, $t0, $t1\n\tsw $t2, ' + regs_for_idents[instruction.get_destination_reg()] + '\n'
        elif operation == 'sub':
            mips = '\tlw $t0, ' + regs_for_idents[instruction.get_source_reg1()] + '\n\tlw $t1, ' + regs_for_idents[
                instruction.get_source_reg2()] + '\n'
            mips = mips + '\tsubu $t2, $t0, $t1\n\tsw $t2, ' + regs_for_idents[instruction.get_destination_reg()] + '\n'
        elif operation == 'mul':
            mips = '\tlw $t0, ' + regs_for_idents[instruction.get_source_reg1()] + '\n\tlw $t1, ' + regs_for_idents[
                instruction.get_source_reg2()] + '\n'
            mips = mips + '\tmulou $t2, $t0, $t1\n\tsw $t2, ' + regs_for_idents[
                instruction.get_destination_reg()] + '\n'
        elif operation == 'div':
            mips = '\tlw $t0, ' + regs_for_idents[instruction.get_source_reg1()] + '\n\tlw $t1, ' + regs_for_idents[
                instruction.get_source_reg2()] + '\n'
            mips = mips + '\tdivu $t2, $t0, $t1\n\tsw $t2, ' + regs_for_idents[instruction.get_destination_reg()] + '\n'
        elif operation == 'rem':
            mips = '\tlw $t0, ' + regs_for_idents[instruction.get_source_reg1()] + '\n\tlw $t1, ' + regs_for_idents[
                instruction.get_source_reg2()] + '\n'
            mips = mips + '\tremu $t2, $t0, $t1\n\tsw $t2, ' + regs_for_idents[instruction.get_destination_reg()] + '\n'
        elif operation == 'seq':
            mips = '\tlw $t0, ' + regs_for_idents[instruction.get_source_reg1()] + '\n\tlw $t1, ' + regs_for_idents[
                instruction.get_source_reg2()] + '\n'
            mips = mips + '\tseq $t2, $t0, $t1\n\tsw $t2, ' + regs_for_idents[instruction.get_destination_reg()] + '\n'
        elif operation == 'sne':
            mips = '\tlw $t0, ' + regs_for_idents[instruction.get_source_reg1()] + '\n\tlw $t1, ' + regs_for_idents[
                instruction.get_source_reg2()] + '\n'
            mips = mips + '\tsne $t2, $t0, $t1\n\tsw $t2, ' + regs_for_idents[instruction.get_destination_reg()] + '\n'
        elif operation == 'slt':
            mips = '\tlw $t0, ' + regs_for_idents[instruction.get_source_reg1()] + '\n\tlw $t1, ' + regs_for_idents[
                instruction.get_source_reg2()] + '\n'
            mips = mips + '\tslt $t2, $t0, $t1\n\tsw $t2, ' + regs_for_idents[instruction.get_destination_reg()] + '\n'
        elif operation == 'sle':
            mips = '\tlw $t0, ' + regs_for_idents[instruction.get_source_reg1()] + '\n\tlw $t1, ' + regs_for_idents[
                instruction.get_source_reg2()] + '\n'
            mips = mips + '\tsle $t2, $t0, $t1\n\tsw $t2, ' + regs_for_idents[instruction.get_destination_reg()] + '\n'
        elif operation == 'sgt':
            mips = '\tlw $t0, ' + regs_for_idents[instruction.get_source_reg1()] + '\n\tlw $t1, ' + regs_for_idents[
                instruction.get_source_reg2()] + '\n'
            mips = mips + '\tsgt $t2, $t0, $t1\n\tsw $t2, ' + regs_for_idents[instruction.get_destination_reg()] + '\n'
        elif operation == 'sge':
            mips = '\tlw $t0, ' + regs_for_idents[instruction.get_source_reg1()] + '\n\tlw $t1, ' + regs_for_idents[
                instruction.get_source_reg2()] + '\n'
            mips = mips + '\tsge $t2, $t0, $t1\n\tsw $t2, ' + regs_for_idents[instruction.get_destination_reg()] + '\n'
        elif operation == 'readint':
            mips = '\tli $v0, 5\n\tsyscall\n\tadd $t0, $v0, $zero\n\tsw $t0, ' + regs_for_idents[
                instruction.get_destination_reg()] + '\n'
        elif operation == 'writeint':
            mips = '\tli $v0, 1\n\tlw $t1, ' + regs_for_idents[
                instruction.get_source_reg1()] + '\n\tadd $a0, $t1, $zero\n\tsyscall\n\tli $v0, 4\n\tla $a0, newline\n\tsyscall\n'
        elif operation == 'cbr':
            mips = '\tlw $t0, ' + regs_for_idents[
                instruction.get_source_reg1()] + '\n\tbne $t0, $zero, ' + instruction.get_label1() + '\n\tj ' + instruction.get_label2() + '\n'
        elif operation == 'jumpl':
            mips = '\tj ' + instruction.get_label1() + '\n'
        elif operation == 'exit':
            mips = '\tli $v0, 10\n\tsyscall\n'
        iloc_instruction = iloc_instruction + mips
        string = string + iloc_instruction

    file_object.write(string)
    block.set_revisited(True)
    if len(block.get_next_blocks()) > 0:
        for child_block in block.get_next_blocks():
            if not child_block.get_revisited():
                generate_mips_code(child_block)


populate_regs_for_idents()
generate_mips_code(starting_block)
file_object.close()
