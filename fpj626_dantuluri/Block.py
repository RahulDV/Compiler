class Block:
    def __init__(self, block_name=None):
        self.block_name = block_name
        self.instructions = []
        self.next_blocks = []
        self.visited = False
        self.revisited = False

    def get_block_name(self):
        return self.block_name

    def set_block_name(self, block_name):
        self.block_name = block_name

    def get_instructions(self):
        return self.instructions

    def add_instructions_to_list(self, instruction):
        self.instructions.append(instruction)

    def get_next_blocks(self):
        return self.next_blocks

    def add_next_block(self, block):
        self.next_blocks.append(block)

    def get_visited(self):
        return self.visited

    def set_visited(self, visited):
        self.visited = visited

    def get_revisited(self):
        return self.revisited

    def set_revisited(self, revisited):
        self.revisited = revisited
