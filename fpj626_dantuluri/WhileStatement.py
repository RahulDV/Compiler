from AST import AST


class WhileStatement(AST):
    def __init__(self, cond_expr=None, while_block_stmt_list=None):
        self.cond_expr = cond_expr
        self.while_block_stmt_list = while_block_stmt_list
        self.type_error = False
        self.node_type = None
        self.data_type = None
        self.name = None
        AST.dot.node(str(self.node_counter), 'While')
        self.gv_name = str(self.node_counter)
        AST.node_counter += 1

    def get_while_block_stmt_list(self):
        return self.while_block_stmt_list

    def set_while_block_stmt_list(self, while_block_stmt_list):
        self.while_block_stmt_list = while_block_stmt_list

    def get_cond_expr(self):
        return self.cond_expr

    def set_cond_expr(self, cond_expr):
        self.cond_expr = cond_expr

    def get_gv_name(self):
        return self.gv_name

    def set_gv_name(self, gv_name):
        self.gv_name = gv_name

    def get_type_error(self):
        return self.type_error

    def set_type_error(self, type_error):
        self.type_error = type_error

    def get_type(self):
        return self.data_type

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def set_type(self, data_type):
        self.data_type = data_type

    def get_node_type(self):
        return self.node_type

    def set_node_type(self, node_type):
        self.node_type = node_type
