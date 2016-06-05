class ASTNode:

    def __init__(self, token, gv_name):
        self.parent = None
        self.child_nodes = []
        self.name = token.getValue()
        self.type = token.getType()
        self.gv_name = gv_name
        self.ident_type = None

    def get_gv_name(self):
        return self.gv_name

    def get_parent(self):
        return self.parent

    def set_parent(self, parent):
        self.parent = parent

    def get_child_nodes(self):
        return self.child_nodes

    def add_to_list_of_children(self, node):
        self.child_nodes.append(node)

    def get_name(self):
        return self.name

    def get_type(self):
        return self.type

    def get_ident_type(self):
        return self.ident_type

    def set_ident_type(self, ident_type):
        self.ident_type = ident_type

