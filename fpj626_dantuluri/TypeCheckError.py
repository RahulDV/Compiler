class TypeCheckError(Exception):
    def __init__(self, ast_node):
        self.ast_node = ast_node

    def __str__(self):
        return repr(self.ast_node)
