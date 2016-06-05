from AST import AST


class AssignStatement(AST):
    def __init__(self, left_expr=None):
        self.left_expr = left_expr
        self.right_expr = None
        self.type_error = False
        self.node_type = None
        self.data_type = None
        self.name = None
        AST.dot.node(str(self.node_counter), ':=')
        self.gv_name = str(self.node_counter)
        AST.node_counter += 1

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

    def get_right_expr(self):
        return self.right_expr

    def set_right_expr(self, right_expr):
        self.right_expr = right_expr

    def get_left_expr(self):
        return self.left_expr

    def set_left_expr(self, left_expr):
        self.left_expr = left_expr

    def get_node_type(self):
        return self.node_type

    def set_node_type(self, node_type):
        self.node_type = node_type
