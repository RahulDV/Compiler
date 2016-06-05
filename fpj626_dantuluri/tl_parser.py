import scanner
import sys
from Node_tl import Node
from ParserError import ParserError
from collections import deque

tokens = scanner.startScanning()

'''for token in tokens:
    print(token.getType() + '(' + token.getValue() + ')')'''

next_token = tokens.pop(0)
stop_declaration = False
declared_variable_list = []

list1 = []


def term(token_param):
    global next_token
    if next_token.getValue() == token_param:
        node = Node(next_token.getValue(), True, next_token)
        try:
            next_token = tokens.pop(0)
        except IndexError:
            return node
        return node
    else:
        raise ParserError("Parsing Error: Expected {}, but received {}".format(token_param, next_token.getValue()))


def term_type(token_param):
    global next_token
    if next_token.getType() == token_param:
        node = Node(next_token.getValue(), True, next_token)
        try:
            next_token = tokens.pop(0)
        except IndexError:
            return node
        return node
    else:
        raise ParserError("Parsing Error: Expected type {}, but received {}".format(token_param, next_token.getValue()))


def identifier(token_param):
    global declared_variable_list
    global next_token
    if next_token.getType() == token_param:
        node = Node(next_token.getType(), True, next_token)
        if not stop_declaration:
            if next_token.getValue() in declared_variable_list:
                raise ParserError('trying to declare same variable again')
            declared_variable_list.append(next_token.getValue())
        else:
            if next_token.getValue() not in declared_variable_list:
                raise ParserError('Using undeclared variable.')
        try:
            next_token = tokens.pop(0)
        except IndexError:
            raise ParserError('Missing END keyword')
        return node
    else:
        raise ParserError('Parsing Error: Expected an identifier')


def program():
    root = None
    children = []
    try:
        if next_token.getValue() == 'program':
            root = Node('<program>')
            children.append(term('program'))
            children.append(declaration())
            children.append(term('begin'))
            children.append(statement_sequence())
            children.append(term('end'))
            root.set_child_nodes(children)
        else:
            raise ParserError(
                "Parser error in program method. Expected 'program' but received {}".format(next_token.getValue()))
    except ParserError as pe:
        print(pe.value)
    return root


def declaration():
    dclr = Node('<declaration>')
    children = []
    if next_token.getValue() == 'begin':
        global stop_declaration
        stop_declaration = True
        children.append(epsilon())
    elif next_token.getValue() == 'var':
        children.append(term('var'))
        children.append(identifier('ident'))
        children.append(term('as'))
        children.append(type_dclr())
        children.append(term(';'))
        children.append(declaration())
    else:
        raise ParserError('declaration parsing failed')
    dclr.set_child_nodes(children)
    return dclr


def epsilon():
    return Node('E', True)


def statement_sequence():
    stsq = Node('<statement_sequence>')
    children = []
    if next_token.getValue() == 'else' or next_token.getValue() == 'end':
        children.append(epsilon())
    elif next_token.getType() == 'ident' or next_token.getValue() == 'if' or next_token.getValue() == 'while' or next_token.getValue() == 'writeint':
        children.append(statement())
        children.append(term(';'))
        children.append(statement_sequence())
    else:
        raise ParserError('statement_sequence parsing failed')
    stsq.set_child_nodes(children)
    return stsq


def type_dclr():
    typdcl = Node('<type>')
    children = []
    if next_token.getValue() == 'int':
        children.append(term('int'))
    elif next_token.getValue() == 'bool':
        children.append(term('bool'))
    else:
        raise ParserError('type_dclr parsing failed')
    typdcl.set_child_nodes(children)
    return typdcl


def statement():
    statement_node = Node('<statement>')
    children = []
    if next_token.getType() == 'ident':
        children.append(assignment())
    elif next_token.getValue() == 'if':
        children.append(if_statement())
    elif next_token.getValue() == 'while':
        children.append(while_statement())
    elif next_token.getValue() == 'writeint':
        children.append(writeint())
    else:
        raise ParserError('statement parsing failed')
    statement_node.set_child_nodes(children)
    return statement_node


def assignment():
    assignment_node = Node('<assignment>')
    children = []
    if next_token.getType() == 'ident':
        children.append(identifier('ident'))
        children.append(term(':='))
        children.append(x())
    else:
        raise ParserError('assignment parsing failed')
    assignment_node.set_child_nodes(children)
    return assignment_node


def x():
    x_node = Node('<x>')
    children = []
    if next_token.getType() == 'ident' or next_token.getType() == 'num' or next_token.getType() == 'boollit' or next_token.getValue() == '(':
        children.append(expression())
    elif next_token.getValue() == 'readint':
        children.append(term('readint'))
    else:
        raise ParserError('x parsing failed')
    x_node.set_child_nodes(children)
    return x_node


def if_statement():
    if_node = Node('<if statement>')
    children = []
    if next_token.getValue() == 'if':
        children.append(term('if'))
        children.append(expression())
        children.append(term('then'))
        children.append(statement_sequence())
        children.append(else_clause())
        children.append(term('end'))
    else:
        raise ParserError('if_statement parsing failed')
    if_node.set_child_nodes(children)
    return if_node


def while_statement():
    node = Node('<while statement>')
    children = []
    if next_token.getValue() == 'while':
        children.append(term('while'))
        children.append(expression())
        children.append(term('do'))
        children.append(statement_sequence())
        children.append(term('end'))
    else:
        raise ParserError('while_statement parsing failed')
    node.set_child_nodes(children)
    return node


def writeint():
    node = Node('<writeint>')
    children = []
    if next_token.getValue() == 'writeint':
        children.append(term('writeint'))
        children.append(expression())
    else:
        raise ParserError('writeint parsing failed')
    node.set_child_nodes(children)
    return node


def expression():
    node = Node('<expression>')
    children = []
    if next_token.getType() == 'ident' or next_token.getType() == 'num' or next_token.getType() == 'boollit' or next_token.getValue() == '(':
        children.append(simple_expression())
        children.append(y())
    else:
        raise ParserError('expression parsing failed')
    node.set_child_nodes(children)
    return node


def else_clause():
    node = Node('<else>')
    children = []
    if next_token.getValue() == 'end':
        children.append(epsilon())
    elif next_token.getValue() == 'else':
        children.append(term('else'))
        children.append(statement_sequence())
    else:
        raise ParserError('else_clause parsing failed')
    node.set_child_nodes(children)
    return node


def simple_expression():
    node = Node('<simple_expression>')
    children = []
    if next_token.getType() == 'ident' or next_token.getType() == 'num' or next_token.getType() == 'boollit' or next_token.getValue() == '(':
        children.append(term_tl())
        children.append(z())
    else:
        raise ParserError('simple_expression parsing failed')
    node.set_child_nodes(children)
    return node


def term_tl():
    node = Node('<term>')
    children = []
    if next_token.getType() == 'ident' or next_token.getType() == 'num' or next_token.getType() == 'boollit' or next_token.getValue() == '(':
        children.append(factor())
        children.append(v())
    else:
        raise ParserError('term_tl parsing failed')
    node.set_child_nodes(children)
    return node


def z():
    node = Node('<z>')
    children = []
    if next_token.getValue() == ';' or next_token.getValue() == 'then' or next_token.getValue() == 'do' or next_token.getType() == 'COMPARE' or next_token.getValue() == ')':
        children.append(epsilon())
    elif next_token.getType() == 'ADDITIVE':
        children.append(term_type('ADDITIVE'))
        children.append(simple_expression())
    else:
        raise ParserError('z parsing failed')
    node.set_child_nodes(children)
    return node


def y():
    node = Node('<y>')
    children = []
    if next_token.getValue() == ';' or next_token.getValue() == 'then' or next_token.getValue() == 'do' or next_token.getValue() == ')':
        children.append(epsilon())
    elif next_token.getType() == 'COMPARE':
        children.append(term_type('COMPARE'))
        children.append(expression())
    else:
        raise ParserError('y parsing failed')
    node.set_child_nodes(children)
    return node


def factor():
    node = Node('<factor>')
    children = []
    if next_token.getType() == 'num':
        children.append(term_type("num"))
    elif next_token.getType() == 'boollit':
        children.append(term_type('boollit'))
    elif next_token.getType() == 'ident':
        children.append(term_type('ident'))
    elif next_token.getValue() == '(':
        children.append(term('('))
        children.append(expression())
        children.append(term(')'))
    else:
        raise ParserError('factor parsing failed')
    node.set_child_nodes(children)
    return node


def v():
    node = Node('<v>')
    children = []
    if next_token.getValue() == ';' or next_token.getValue() == 'then' or next_token.getValue() == 'do' or next_token.getValue() == ')' or next_token.getType() == 'ADDITIVE' or next_token.getType() == 'COMPARE':
        children.append(epsilon())
    elif next_token.getType() == 'MULTIPLICATIVE':
        children.append(term_type('MULTIPLICATIVE'))
        children.append(term_tl())
    else:
        raise ParserError('v parsing failed')
    node.set_child_nodes(children)
    return node


def parse1():
    global list1
    list1 = program()
    return list1


queue = deque()


def print_tree(nd):
    level = 0
    queue.append(nd)
    while len(queue) > 0:
        node = queue.popleft()
        print(node.get_name())
        if not node.get_terminal():
            for n in node.get_child_nodes():
                queue.append(n)


def print_preorder(node):
    print(node.get_name())
    children = node.get_child_nodes()
    while len(children) > 0:
        child = children.pop(0)
        if not child.get_terminal():
            print_preorder(child)
        else:
            print(child.get_name())


'''print_preorder(parse1())'''
