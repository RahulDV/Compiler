from collections import deque
from mytoken import Token
import sys

buffer = deque(maxlen=20)
eof = False

source_file_name = sys.argv[1]

save_to_file_switch = False
list_of_tokens = []
fileobject = open(source_file_name, 'r')
fileobject2 = open('token.txt', 'w')


def load_buffer():
    while len(buffer) < buffer.maxlen:
        char_read = fileobject.read(1)
        if char_read == '':
            if len(buffer) <= 0:
                global eof
                eof = True
            break
        buffer.append(char_read)


keyword_list = (
'if', 'then', 'else', 'begin', 'end', 'while', 'do', 'program', 'var', 'as', 'int', 'bool', 'writeint', 'readint')
bool_liter_list = ('true', 'false')
operators = ('div', 'mod')


def tokenize(char_list_param, type):
    value = ''
    for ch in char_list_param:
        value += ch
    if type == 'KEYWORD':
        if value in keyword_list:
            # value = value.upper()
            return Token(type=type, value=value)
        elif value in bool_liter_list:
            return Token(type='boollit', value=value)
        elif value in operators:
            return Token(type='MULTIPLICATIVE', value=value)
        else:
            return False
    else:
        return Token(type=type, value=value)


numeral_fsm = [[2, 1, 3], [1, 1, 3], [3, 3, 3]]


def numerals(char_param):
    accepted_chars = []
    current_state = 0
    ascii = ord(char_param)
    column_val = 2
    if ascii == 48:
        column_val = 0
    elif (ascii >= 49) and (ascii <= 57):
        column_val = 1
    current_state = numeral_fsm[current_state][column_val]
    if current_state == 3:
        return False
    else:
        accepted_chars.append(char_param)
        while not eof:
            try:
                next_char = buffer.popleft()
                next_char_ascii = ord(next_char)
                if next_char_ascii == 9 or next_char_ascii == 13 or next_char_ascii == 32 or next_char_ascii == 10:
                    return tokenize(accepted_chars, 'num')
                elif next_char_ascii == 48:
                    column_val = 0
                elif (next_char_ascii >= 49) and (next_char_ascii <= 57):
                    column_val = 1
                else:
                    column_val = 2
                current_state = numeral_fsm[current_state][column_val]
                if current_state == 3:
                    return False
                else:
                    accepted_chars.append(next_char)
            except IndexError:
                load_buffer()
                continue
        else:
            if len(accepted_chars) > 0:
                return tokenize(accepted_chars, 'num')


keyword_fsm = [[1, 2], [1, 2]]


def keywords(char_param):
    accepted_chars = []
    current_state = 0
    ascii = ord(char_param)
    column_val = 1
    if (ascii >= 97) and (ascii <= 122):
        column_val = 0
    else:
        column_val == 1
    current_state = keyword_fsm[current_state][column_val]
    if current_state == 2:
        return False
    else:
        accepted_chars.append(char_param)

    while not eof:
        try:
            next_char = buffer.popleft()
            next_char_ascii = ord(next_char)
            if next_char_ascii == 9 or next_char_ascii == 13 or next_char_ascii == 32 or next_char_ascii == 10:
                return tokenize(accepted_chars, 'KEYWORD')
            elif (next_char_ascii >= 97) and (next_char_ascii <= 122):
                column_val = 0
            else:
                column_val = 1
            current_state = keyword_fsm[current_state][column_val]
            if current_state == 2:
                return False
            else:
                accepted_chars.append(next_char)
        except IndexError:
            load_buffer()
            continue
    else:
        if len(accepted_chars) > 0:
            return tokenize(accepted_chars, 'KEYWORD')


comment_fsm = [[1, 3, 3], [1, 1, 2]]


def comment(char_param):
    current_state = 0
    ascii = ord(char_param)
    column_val = 1
    if ascii == 10 or ascii == 13:
        column_val = 2
    elif ascii == 37:
        column_val = 0
    current_state = comment_fsm[current_state][column_val]
    if current_state == 3:
        return False

    while not eof:
        try:
            next_char = buffer.popleft()
            next_char_ascii = ord(next_char)
            if next_char_ascii == 10 or next_char_ascii == 13:
                column_val = 2
            elif next_char_ascii == 37:
                column_val = 0
            else:
                column_val = 1
            current_state = comment_fsm[current_state][column_val]
            if current_state == 2:
                break
        except IndexError:
            load_buffer()
            continue


iden_fsm = [[1, 2, 2], [1, 1, 2]]


def identifier(char_param):
    accepted_chars = []
    current_state = 0
    ascii = ord(char_param)
    column_val = 2
    if (ascii >= 65) and (ascii <= 90):
        column_val = 0
    elif (ascii >= 48) and (ascii <= 57):
        column_val = 1
    current_state = iden_fsm[current_state][column_val]
    if current_state == 2:
        return False
    else:
        accepted_chars.append(char_param)

    while not eof:
        try:
            next_char = buffer.popleft()
            next_char_ascii = ord(next_char)
            if next_char_ascii == 9 or next_char_ascii == 13 or next_char_ascii == 32 or next_char_ascii == 10:
                return tokenize(accepted_chars, 'ident')
            elif (next_char_ascii >= 65) and (next_char_ascii <= 90):
                column_val = 0
            elif (next_char_ascii >= 48) and (next_char_ascii <= 57):
                column_val = 1
            else:
                column_val = 2
            current_state = iden_fsm[current_state][column_val]
            if current_state == 2:
                return False
            else:
                accepted_chars.append(next_char)
        except IndexError:
            load_buffer()
            continue
    else:
        if len(accepted_chars) > 0:
            return tokenize(accepted_chars, 'ident')


operator_dict = {'>': 'COMPARE', '<': 'COMPARE', '>=': 'COMPARE', '<=': 'COMPARE', '=': 'COMPARE', '!=': 'COMPARE',
                 '+': 'ADDITIVE', '-': 'ADDITIVE', '*': 'MULTIPLICATIVE', '(': 'LP', ')': 'RP', ':=': 'ASGN', ';': 'SC'}


def symbols_operators(char_param):
    token = False
    accept_chars = []
    accept_chars.append(char_param)
    while not eof:
        try:
            next_char = buffer.popleft()
            next_char_ascii = ord(next_char)
            if next_char_ascii == 9 or next_char_ascii == 13 or next_char_ascii == 32 or next_char_ascii == 10:
                token = tokenize(accept_chars, 'OPERATOR')
                break
            else:
                accept_chars.append(next_char)
        except IndexError:
            load_buffer()
            continue
    if not token:
        return False
    elif token.getValue() in operator_dict:
        token.setType(operator_dict.get(token.getValue()))
        return token
    else:
        return False


def persisttoken(token):
    try:
        if save_to_file_switch:
            fileobject2.write(token.getType() + '(' + token.getValue() + ')\n')
        else:
            list_of_tokens.append(token)
        return True
    except IOError:
        print('could not persist token {} into token file'.token.getValue())
        return False


def persisttoken2(token):
    try:
        if save_to_file_switch:
            fileobject2.write(token.getValue() + '\n')
        else:
            list_of_tokens.append(token)
        return True
    except IOError:
        print('could not persist token {} into token file'.token.getValue())
        return False


'''
while not eof:
    token = False
    try:
        character =  buffer.popleft()
        ascii = ord(character)
        if ascii == 9 or ascii == 13 or ascii == 32 or ascii == 10:
            continue
        if ascii == 37:
            comment(character)
        else:
            if (ascii >= 65) and (ascii <= 90):
                token = identifier(character)
            elif (ascii >= 97) and (ascii <= 122):
                token = keywords(character)
            elif (ascii >= 48) and (ascii <= 57):
                token = numerals(character)
            else:
                token = symbols_operators(character)
            if not token:
                print("Lexical error while tokenizing {}".format(character))
                fileobject2.write("Lexical error while tokenizing {}".format(character))
                break
            else:
                if token.getType() == 'KEYWORD':
                    persist = persisttoken2(token)
                else:
                    persist = persisttoken(token)
                if not persist:
                    break
    except IndexError:
        load_buffer()
        continue
'''


def startScanning():
    while not eof:
        token = False
        try:
            character = buffer.popleft()
            ascii = ord(character)
            if ascii == 9 or ascii == 13 or ascii == 32 or ascii == 10:
                continue
            if ascii == 37:
                comment(character)
            else:
                if (ascii >= 65) and (ascii <= 90):
                    token = identifier(character)
                elif (ascii >= 97) and (ascii <= 122):
                    token = keywords(character)
                elif (ascii >= 48) and (ascii <= 57):
                    token = numerals(character)
                else:
                    token = symbols_operators(character)
                if not token:
                    print("Lexical error while tokenizing {}".format(character))
                    fileobject2.write("Lexical error while tokenizing {}".format(character))
                    break
                else:
                    if token.getType() == 'KEYWORD':
                        persist = persisttoken2(token)
                    else:
                        persist = persisttoken(token)
                    if not persist:
                        break
        except IndexError:
            load_buffer()
            continue
    fileobject.close()
    fileobject2.close()
    return list_of_tokens
