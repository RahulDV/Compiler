import tl_parser
from ast_node import ASTNode
from graphviz import Graph
from TypeCheckError import TypeCheckError
from Program import Program
from Declaration import Declaration
from Dclr_List import DclrList
from Stmt_List import StmtList
from Expression import Expression
from AssignStatement import AssignStatement
from WhileStatement import WhileStatement
from IfStatement import IfStatement
from Statement import Statement
from AST import AST
import sys

#root = tl_parser.parse1()

dot2 = Graph(comment='Abstract Syntax Tree')
node_counter = 0


def generate_ast(node):
    global node_counter
    children = node.get_child_nodes()
    child0 = children.pop(0)
    while child0.get_name() == 'E':
        if len(children) > 0:
            child0 = children.pop(0)
        else:
            return None
    if child0.get_terminal():
        parent_ast = ASTNode(child0.get_token(), str(node_counter))
        node_counter += 1
    else:
        parent_ast = generate_ast(child0)
        while parent_ast is None and len(children) > 0:
            parent_ast = generate_ast(children.pop(0))
    dot2.node(parent_ast.get_gv_name(), parent_ast.get_name())
    while len(children) > 0:
        child = children.pop(0)
        if child.get_name() == 'E':
            continue
        elif child.get_terminal():
            ast = ASTNode(child.get_token(), str(node_counter))
            node_counter += 1
        else:
            ast = generate_ast(child)
            while ast is None and len(children) > 0:
                ast = generate_ast(children.pop(0))
        if ast is not None:
            dot2.node(ast.get_gv_name(), ast.get_name())
            ast.set_parent(parent_ast)
            parent_ast.add_to_list_of_children(ast)
            dot2.edge(parent_ast.get_gv_name(), ast.get_gv_name())
    return parent_ast


#ast_root = generate_ast(root)
symbol_table = {}


def generate_symbol_table(node):
    global symbol_table
    var = node.get_child_nodes()[0]
    while var is not None:
        try:
            symbol_table[var.get_child_nodes()[0].get_name()] = var.get_child_nodes()[2].get_name()
            var = var.get_child_nodes()[4]
        except IndexError:
            break
    symbol_table['readint'] = 'int'


#generate_symbol_table(ast_root)


def convert_to_ast(node):
    program = Program()
    program.set_name(node.get_name())
    program.set_type(node.get_type())
    dclr_child = node.get_child_nodes()[0]
    dclr_list = DclrList()
    while True:
        if dclr_child is not None and dclr_child.get_name() == 'var':
            ident_name = dclr_child.get_child_nodes()[0]
            declaration = Declaration(ident_name.get_name())
            declaration.set_name(ident_name.get_name())
            declaration.set_type(symbol_table.get(ident_name.get_name()))
            dclr_list.add_declaration_to_list(declaration)
            AST.dot.edge(dclr_list.get_gv_name(), declaration.get_gv_name())
            length = len(dclr_child.get_child_nodes())
            dclr_child = dclr_child.get_child_nodes()[length - 1]
        else:
            break
    program.set_dclr_list(dclr_list)
    AST.dot.edge(program.get_gv_name(), dclr_list.get_gv_name())
    stmt_child = node.get_child_nodes()[2]
    stmt_list = generate_statement_list(stmt_child)
    if stmt_list.get_type_error():
        AST.dot.edge(program.get_gv_name(), stmt_list.get_gv_name(), color='red')
    else:
        AST.dot.edge(program.get_gv_name(), stmt_list.get_gv_name())
    program.set_stmt_list(stmt_list)
    return program


def generate_statement_list(param_node):
    node = param_node
    stmt_list = StmtList()
    while True:
        if node.get_type() == 'ident':
            left_expr = Expression(node.get_name())
            left_expr.set_type(symbol_table.get(node.get_name()))
            left_expr.set_node_type(node.get_type())
            assign_stmt = AssignStatement(left_expr)
            assign_name = node.get_child_nodes()[0].get_name()
            assign_stmt.set_name(assign_name)
            right_expr = evaluate_expression(node.get_child_nodes()[1])
            assign_stmt.set_right_expr(right_expr)
            stmt_list.add_statement_to_list(assign_stmt)
            if (not right_expr.get_type_error()) and (left_expr.get_type() == right_expr.get_type()):
                AST.dot.edge(stmt_list.get_gv_name(), assign_stmt.get_gv_name())
                AST.dot.edge(assign_stmt.get_gv_name(), left_expr.get_gv_name())
                AST.dot.edge(assign_stmt.get_gv_name(), right_expr.get_gv_name())
                assign_stmt.set_type(left_expr.get_type())
            else:
                AST.dot.edge(stmt_list.get_gv_name(), assign_stmt.get_gv_name(), color='red')
                AST.dot.edge(assign_stmt.get_gv_name(), left_expr.get_gv_name(), color='red')
                AST.dot.edge(assign_stmt.get_gv_name(), right_expr.get_gv_name(), color='red')
                stmt_list.set_type_error(True)

        elif node.get_name() == 'while' or node.get_name() == 'if':
            child0 = node.get_child_nodes()[0]
            length = len(child0.get_child_nodes())
            if length > 1:
                left_expr = evaluate_expression(child0)
                child = child0.get_child_nodes()[1]
            else:
                left_expr = Expression(child0.get_name())
                left_expr.set_type(symbol_table.get(child0.get_name()))
                left_expr.set_node_type(child0.get_type())
                child = child0.get_child_nodes()[0]
            compare_expr = Expression(child.get_name())
            compare_expr.set_type('bool')
            right_expr = evaluate_expression(child.get_child_nodes()[0])
            if (not left_expr.get_type_error()) and (not right_expr.get_type_error()) and (left_expr.get_type() == right_expr.get_type()):
                AST.dot.edge(compare_expr.get_gv_name(), left_expr.get_gv_name())
                AST.dot.edge(compare_expr.get_gv_name(), right_expr.get_gv_name())
            else:
                if (not left_expr.get_type_error()) and (not right_expr.get_type_error()) and (left_expr.get_type() != right_expr.get_type()):
                    AST.dot.edge(compare_expr.get_gv_name(), left_expr.get_gv_name(), color='red')
                    AST.dot.edge(compare_expr.get_gv_name(), right_expr.get_gv_name(), color='red')
                else:
                    if left_expr.get_type_error():
                        AST.dot.edge(compare_expr.get_gv_name(), left_expr.get_gv_name(), color='red')
                    else:
                        AST.dot.edge(compare_expr.get_gv_name(), left_expr.get_gv_name())
                    if right_expr.get_type_error():
                        AST.dot.edge(compare_expr.get_gv_name(), right_expr.get_gv_name(), color='red')
                    else:
                        AST.dot.edge(compare_expr.get_gv_name(), right_expr.get_gv_name())
                compare_expr.set_type_error(True)
            compare_expr.set_left_expr(left_expr)
            compare_expr.set_right_expr(right_expr)

            if node.get_name() == 'while':
                while_statement = WhileStatement(compare_expr)
                while_statement.set_name(node.get_name())
                while_statement.set_node_type(node.get_type())
                st_lst = generate_statement_list(node.get_child_nodes()[2])
                while_statement.set_while_block_stmt_list(st_lst)
                stmt_list.add_statement_to_list(while_statement)
                if compare_expr.get_type_error() or st_lst.get_type_error():
                    AST.dot.edge(stmt_list.get_gv_name(), while_statement.get_gv_name(), color='red')
                    if compare_expr.get_type_error():
                        AST.dot.edge(while_statement.get_gv_name(), compare_expr.get_gv_name(), color='red')
                    else:
                        AST.dot.edge(while_statement.get_gv_name(), compare_expr.get_gv_name())
                    if st_lst.get_type_error():
                        AST.dot.edge(while_statement.get_gv_name(), st_lst.get_gv_name(), color='red')
                    else:
                        AST.dot.edge(while_statement.get_gv_name(), st_lst.get_gv_name())
                    stmt_list.set_type_error(True)
                else:
                    AST.dot.edge(stmt_list.get_gv_name(), while_statement.get_gv_name())
                    AST.dot.edge(while_statement.get_gv_name(), compare_expr.get_gv_name())
                    AST.dot.edge(while_statement.get_gv_name(), st_lst.get_gv_name())
            else:
                if_statement = IfStatement(compare_expr)
                if_statement.set_name(node.get_name())
                if_statement.set_node_type(node.get_type())
                then_block = node.get_child_nodes()[2]
                else_block = node.get_child_nodes()[3].get_child_nodes()[0]
                then_lst = generate_statement_list(then_block)
                else_lst = generate_statement_list(else_block)
                if_statement.set_if_block_stmt_list(then_lst)
                if_statement.set_else_block_stmt_list(else_lst)
                stmt_list.add_statement_to_list(if_statement)
                if compare_expr.get_type_error() or then_lst.get_type_error() or else_lst.get_type_error():
                    AST.dot.edge(stmt_list.get_gv_name(), if_statement.get_gv_name(), color='red')
                    if compare_expr.get_type_error():
                        AST.dot.edge(if_statement.get_gv_name(), compare_expr.get_gv_name(), color='red')
                    else:
                        AST.dot.edge(if_statement.get_gv_name(), compare_expr.get_gv_name())
                    if then_lst.get_type_error():
                        AST.dot.edge(if_statement.get_gv_name(), then_lst.get_gv_name(), color='red')
                    else:
                        AST.dot.edge(if_statement.get_gv_name(), then_lst.get_gv_name())
                    if else_lst.get_type_error():
                        AST.dot.edge(if_statement.get_gv_name(), else_lst.get_gv_name(), color='red')
                    else:
                        AST.dot.edge(if_statement.get_gv_name(), else_lst.get_gv_name())
                    stmt_list.set_type_error(True)
                else:
                    AST.dot.edge(stmt_list.get_gv_name(), if_statement.get_gv_name())
                    AST.dot.edge(if_statement.get_gv_name(), compare_expr.get_gv_name())
                    AST.dot.edge(if_statement.get_gv_name(), then_lst.get_gv_name())
                    AST.dot.edge(if_statement.get_gv_name(), else_lst.get_gv_name())

        elif node.get_name() == 'writeint':
            expr = evaluate_expression(node.get_child_nodes()[0])
            statement = Statement(expr)
            statement.set_name(node.get_name())
            stmt_list.add_statement_to_list(statement)
            if (not expr.get_type_error()) and (expr.get_type() == 'int'):
                AST.dot.edge(stmt_list.get_gv_name(), statement.get_gv_name())
                AST.dot.edge(statement.get_gv_name(), expr.get_gv_name())
            else:
                AST.dot.edge(stmt_list.get_gv_name(), statement.get_gv_name(), color='red')
                AST.dot.edge(statement.get_gv_name(), expr.get_gv_name(), color='red')
                stmt_list.set_type_error(True)
        else:
            break;

        length = len(node.get_child_nodes())
        node = node.get_child_nodes()[length - 1]

    return stmt_list


def evaluate_expression(node):
    if node.get_name() == '(':
        length = len(node.get_child_nodes())
        left_expr = evaluate_expression(node.get_child_nodes()[0])
        if length == 3:
            child = node.get_child_nodes()[2]
            expr = Expression(child.get_name())
            expr.set_node_type(child.get_type())
            right_expr = evaluate_expression(child.get_child_nodes()[0])
            expr.set_left_expr(left_expr)
            expr.set_right_expr(right_expr)
            if (not left_expr.get_type_error()) and (not right_expr.get_type_error()) and left_expr.get_type() == right_expr.get_type():
                AST.dot.edge(expr.get_gv_name(), left_expr.get_gv_name())
                AST.dot.edge(expr.get_gv_name(), right_expr.get_gv_name())
                expr.set_type(left_expr.get_type())
            else:
                if (not left_expr.get_type_error()) and (not right_expr.get_type_error()) and left_expr.get_type() != right_expr.get_type():
                    AST.dot.edge(expr.get_gv_name(), left_expr.get_gv_name(), color='red')
                    AST.dot.edge(expr.get_gv_name(), right_expr.get_gv_name(), color='red')
                else:
                    if left_expr.get_type_error():
                        AST.dot.edge(expr.get_gv_name(), left_expr.get_gv_name(), color='red')
                    else:
                        AST.dot.edge(expr.get_gv_name(), left_expr.get_gv_name())
                    if right_expr.get_type_error():
                        AST.dot.edge(expr.get_gv_name(), right_expr.get_gv_name(), color='red')
                    else:
                        AST.dot.edge(expr.get_gv_name(), right_expr.get_gv_name())
                expr.set_type_error(True)
            return expr
        else:
            return left_expr
    else:
        left_expr = Expression(node.get_name())
        if node.get_type() == 'num':
            left_expr.set_type('int')
        elif node.get_type() == 'bool':
            left_expr.set_type('bool')
        else:
            left_expr.set_type(symbol_table.get(node.get_name()))
        left_expr.set_node_type(node.get_type())
        if len(node.get_child_nodes()) <= 0:
            return left_expr;
        child = node.get_child_nodes()[0]
        expr = Expression(child.get_name())
        expr.set_node_type(child.get_type())
        expr.set_left_expr(left_expr)
        child2 = child.get_child_nodes()[0]
        if len(child2.get_child_nodes()) > 0:
            right_expr = evaluate_expression(child2)
        else:
            right_expr = Expression(child2.get_name())
            if child2.get_type() == 'num':
                right_expr.set_type('int')
            elif child2.get_type() == 'bool':
                right_expr.set_type('bool')
            else:
                right_expr.set_type(symbol_table.get(child2.get_name()))
            right_expr.set_node_type(child2.get_type())
        if (not right_expr.get_type_error()) and (left_expr.get_type() == right_expr.get_type()):
            AST.dot.edge(expr.get_gv_name(), left_expr.get_gv_name())
            AST.dot.edge(expr.get_gv_name(), right_expr.get_gv_name())
            expr.set_type(left_expr.get_type())
        else:
            if (not right_expr.get_type_error()) and (left_expr.get_type() != right_expr.get_type()):
                AST.dot.edge(expr.get_gv_name(), left_expr.get_gv_name(), color='red')
                AST.dot.edge(expr.get_gv_name(), right_expr.get_gv_name(), color='red')
            else:
                if right_expr.get_type_error():
                    AST.dot.edge(expr.get_gv_name(), right_expr.get_gv_name(), color='red')
                    AST.dot.edge(expr.get_gv_name(), left_expr.get_gv_name())
            expr.set_type_error(True)
        expr.set_right_expr(right_expr)
        return expr


#program = convert_to_ast(ast_root)




def type_checking(node):
    if node.get_name() == 'program':
        type_checking(node.get_child_nodes()[2])
    elif node.get_type() == 'ident':
        check_assignment(node)
        children = node.get_child_nodes()
        last_child = children[len(children) - 1]
        if last_child.get_name() != ';':
            type_checking(last_child)
    elif node.get_name() == 'while':
        child0 = node.get_child_nodes()[0]
        check_assignment(child0)
        children = node.get_child_nodes()
        type_checking(children[2])
        last_child = children[len(children) - 1]
        if last_child.get_name() != ';':
            type_checking(last_child)
    elif node.get_name() == 'if':
        child0 = node.get_child_nodes()[0]
        check_assignment(child0)
        children = node.get_child_nodes()
        type_checking(children[2])
        else_node = children[3]
        type_checking(else_node.get_child_nodes()[0])
        last_child = children[len(children) - 1]
        if last_child.get_name() != ';':
            type_checking(last_child)
    elif node.get_name() == 'writeint':
        child0 = node.get_child_nodes()[0]
        if len(child0.get_child_nodes()) > 0:
            check_assignment(child0)
        if child0.get_ident_type() is None:
            ch_type = symbol_table[child0.get_name()]
        else:
            ch_type = child0.get_ident_type()
        if ch_type == 'bool':
            raise TypeCheckError(child0)


def check_assignment(node):
    child1 = node.get_child_nodes()[0]
    if child1.get_name() == ':=':
        rhs = node.get_child_nodes()[1]
    elif (child1.get_type() == 'MULTIPLICATIVE') or (child1.get_type() == 'ADDITIVE' or 'COMPARE'):
        rhs = child1.get_child_nodes()[0]
    else:
        return
    if len(rhs.get_child_nodes()) > 0:
        temp = rhs
        while temp.get_name() == '(':
            temp = temp.get_child_nodes()[0]
        check_assignment(temp)
        if rhs.get_name() == '(':
            rhs.set_ident_type(temp.get_ident_type())
    if rhs.get_type() == 'num':
        rhs_type = 'int'
    elif rhs.get_ident_type() is None:
        rhs_type = symbol_table[rhs.get_name()]
    else:
        rhs_type = rhs.get_ident_type()
    if node.get_type() == 'num':
        lhs_type = 'int'
    elif node.get_ident_type() is None:
        lhs_type = symbol_table[node.get_name()]
    else:
        lhs_type = node.get_ident_type()
    if rhs_type != lhs_type:
        raise TypeCheckError(rhs)
    node.set_ident_type(rhs_type)


def start():
    root = tl_parser.parse1()
    ast_root = generate_ast(root)
    generate_symbol_table(ast_root)
    result = convert_to_ast(ast_root)
    ast_dest_file = sys.argv[2]
    fileobject2 = open(ast_dest_file, 'w')
    fileobject2.write(AST.dot.source)
    fileobject2.close()
    return result

# dest_file_name = sys.argv[2]
'''
try:
    type_checking(ast_root)
except TypeCheckError as tc:
    ast = tc.ast_node
    print("Type mismatch exception. Check the generated tree for error")
    while ast.get_parent() is not None:
        dot2.edge(ast.get_parent().get_gv_name(), ast.get_gv_name(), color='red')
        ast = ast.get_parent()

fileobject2.write(AST.dot.source)
# print(dot.source)
fileobject2.close()

def print_preorder(node):
    print(node.get_name())
    children = node.get_child_nodes()
    while len(children) > 0:
        child = children.pop(0)
        if len(child.get_child_nodes()) > 0:
            print_preorder(child)
        else:
            print(child.get_name())

print_preorder(ast_root)
'''
