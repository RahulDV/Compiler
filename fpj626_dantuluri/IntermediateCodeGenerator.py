import ast_generator
from collections import deque
from Block import Block
from Instruction import Instruction
from graphviz import Digraph
import sys

program = ast_generator.start()
print(program)

reg_queue = deque()
register_counter = 0


def get_register():
    global register_counter
    '''if len(reg_queue) > 0:
        reg = reg_queue.popleft()
    else:'''
    reg = register_counter
    register_counter += 1
    return reg


def add_registers_to_queue(register):
    global reg_queue
    if register not in reg_queue:
        reg_queue.append(register)


ident_regs = {}


def allocate_reg_to_identifiers(dclr_list):
    global ident_regs
    i = 0
    declarations = dclr_list.get_declarations()
    while i < len(declarations):
        declaration = declarations[i]
        ident_regs[declaration.get_identifier()] = 'r_' + declaration.get_identifier()
        i += 1


def get_ident_regs():
    global ident_regs
    return ident_regs


block_counter = 1


def generate_3address_code(statement_list):
    global block_counter
    block = Block('B' + str(block_counter))
    head = block
    block_counter += 1
    i = 0
    statements = statement_list.get_statements()
    while i < len(statements):
        statement = statements[i]
        if statement.get_name() == ':=':
            left_expr = evaluate_expr(statement.get_left_expr(), block)
            right_expr = evaluate_expr(statement.get_right_expr(), block)
            instruction = Instruction('mov')
            instruction.set_source_reg1(right_expr.get_register())
            instruction.set_destination_reg(left_expr.get_register())
            block.add_instructions_to_list(instruction)
        elif statement.get_name() == 'while':
            block2 = Block('B' + str(block_counter))
            block_counter += 1
            jump_instr = Instruction('jumpl')
            jump_instr.set_label1(block2.get_block_name())
            block.add_instructions_to_list(jump_instr)
            block.add_next_block(block2)
            cond_expr = evaluate_expr(statement.get_cond_expr(), block2)
            success_block = generate_3address_code(statement.get_while_block_stmt_list())
            success_block.add_instructions_to_list(jump_instr)
            success_block.add_next_block(block2)
            instruction = Instruction('cbr')
            instruction.set_source_reg1(cond_expr.get_register())
            instruction.set_label1(success_block.get_block_name())
            block = Block('B' + str(block_counter))
            block_counter += 1
            instruction.set_label2(block.get_block_name())
            block2.add_instructions_to_list(instruction)
            block2.add_next_block(success_block)
            block2.add_next_block(block)
        elif statement.get_name() == 'if':
            block2 = Block('B' + str(block_counter))
            block_counter += 1
            jump_instr = Instruction('jumpl')
            jump_instr.set_label1(block2.get_block_name())
            block.add_instructions_to_list(jump_instr)
            block.add_next_block(block2)
            cond_expr = evaluate_expr(statement.get_cond_expr(), block2)
            if_block = generate_3address_code(statement.get_if_block_stmt_list())
            else_block = generate_3address_code(statement.get_else_block_stmt_list())
            instruction = Instruction('cbr')
            instruction.set_source_reg1(cond_expr.get_register())
            instruction.set_label1(if_block.get_block_name())
            instruction.set_label2(else_block.get_block_name())
            block2.add_instructions_to_list(instruction)
            block2.add_next_block(if_block)
            block2.add_next_block(else_block)
            j = i + 1
            if j < len(statements):
                block = Block('B' + str(block_counter))
                block_counter += 1
                jump_instr.set_label1(block.get_block_name())
                if_block.add_instructions_to_list(jump_instr)
                else_block.add_instructions_to_list(jump_instr)
                if_block.add_next_block(block)
                else_block.add_next_block(block)
        else:
            expr = evaluate_expr(statement.get_expr(), block)
            instruction = Instruction('writeint')
            instruction.set_source_reg1(expr.get_register())
            block.add_instructions_to_list(instruction)
        i += 1

    return head


def evaluate_expr(expr, block):
    if expr.get_node_type() == 'ident':
        expr.set_register(ident_regs[expr.get_name()])
    else:
        if expr.get_node_type() == 'num':
            instruction = Instruction('movi')
            instruction.set_immediate(expr.get_name())
        elif expr.get_node_type() == 'bool':
            if expr.expr.get_name() == 'false':
                numvalue = '0'
            else:
                numvalue = '1'
            instruction = Instruction('movi')
            instruction.set_immediate(numvalue)
        elif expr.get_name() == 'readint':
            instruction = Instruction('readint')
        else:
            if expr.get_name() == '+':
                instruction = Instruction('add')
            elif expr.get_name() == '*':
                instruction = Instruction('mul')
            elif expr.get_name() == '-':
                instruction = Instruction('sub')
            elif expr.get_name() == 'div':
                instruction = Instruction('div')
            elif expr.get_name() == 'mod':
                instruction = Instruction('rem')
            elif expr.get_name() == '=':
                instruction = Instruction('seq')
            elif expr.get_name() == '!=':
                instruction = Instruction('sne')
            elif expr.get_name() == '<':
                instruction = Instruction('slt')
            elif expr.get_name() == '<=':
                instruction = Instruction('sle')
            elif expr.get_name() == '>':
                instruction = Instruction('sgt')
            elif expr.get_name() == '>=':
                instruction = Instruction('sge')
            left_expr = evaluate_expr(expr.get_left_expr(), block)
            right_expr = evaluate_expr(expr.get_right_expr(), block)
            instruction.set_source_reg1(left_expr.get_register())
            instruction.set_source_reg2(right_expr.get_register())
            add_registers_to_queue(left_expr.get_register())
            add_registers_to_queue(right_expr.get_register())
        reg = get_register()
        instruction.set_destination_reg(reg)
        block.add_instructions_to_list(instruction)
        expr.set_register(reg)
    return expr


dot = Digraph(comment='Control Flow Graph')


def print_cfg(block):
    if block is not None:
        i = 0
        instructions = block.get_instructions()
        label = '{}\n'.format(block.get_block_name())
        while i < len(block.get_instructions()):
            instruction = instructions[i]
            if instruction.get_label1() == ' ':
                sublabel = '{} {} {} {} => {}\n'.format(instruction.get_operation(), instruction.get_source_reg1(),
                                                        instruction.get_source_reg2(), instruction.get_immediate(),
                                                        instruction.get_destination_reg())
            else:
                sublabel = '{} {} {} -> {} {}\n'.format(instruction.get_operation(), instruction.get_source_reg1(),
                                                        instruction.get_source_reg2(), instruction.get_label1(),
                                                        instruction.get_label2())
            label = label + sublabel
            i += 1
        dot.node(block.get_block_name(), label, shape='box')
        block.set_visited(True)
        child_blocks = block.get_next_blocks()
        no_of_child_blocks = len(child_blocks)
        if no_of_child_blocks > 0:
            for child_block in child_blocks:
                if not child_block.get_visited():
                    print_cfg(child_block)
                dot.edge(block.get_block_name(), child_block.get_block_name())
        else:
            instruction = Instruction('exit')
            block.add_instructions_to_list(instruction)
            dot.node('exit', 'exit')
            dot.edge(block.get_block_name(), 'exit')
    return


def start():
    allocate_reg_to_identifiers(program.get_dclr_list())
    block = generate_3address_code(program.get_stmt_list())
    print_cfg(block)
    cfg_dest_file = sys.argv[3]
    file_object = open(cfg_dest_file, 'w')
    file_object.write(dot.source)
    file_object.close()
    return block


'''start()'''
