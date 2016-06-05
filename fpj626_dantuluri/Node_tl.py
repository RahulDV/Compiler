# This class is used as a tree data structure. From compiler point of view this is a parse tree.

class Node:
    def __init__(self, name=None, terminal=False, token=None):
        self.terminal = terminal
        self.name = name
        self.token = token
        self.child_nodes = None

    def get_terminal(self):
        return self.terminal

    def set_terminal(self, terminal):
        self.terminal = terminal

    def get_child_nodes(self):
        return self.child_nodes

    def set_child_nodes(self, child_nodes):
        self.child_nodes = child_nodes

    def get_token(self):
        return self.token

    def set_token(self, token):
        self.token = token

    def get_name(self):
        return self.name
