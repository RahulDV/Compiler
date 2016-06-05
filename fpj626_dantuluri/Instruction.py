class Instruction:
    def __init__(self, operation=None):
        self.operation = operation
        self.source_reg1 = ' '
        self.source_reg2 = ' '
        self.immediate = ' '
        self.destination_reg = ' '
        self.label1 = ' '
        self.label2 = ' '

    def get_label1(self):
        return self.label1

    def set_label1(self, label):
        self.label1 = label

    def get_label2(self):
        return self.label2

    def set_label2(self, label):
        self.label2 = label

    def get_operation(self):
        return self.operation

    def get_source_reg1(self):
        return self.source_reg1

    def get_source_reg2(self):
        return self.source_reg2

    def get_immediate(self):
        return self.immediate

    def get_destination_reg(self):
        return self.destination_reg

    def set_operation(self, operation):
        self.operation = operation

    def set_source_reg1(self, source_reg1):
        self.source_reg1 = source_reg1

    def set_source_reg2(self, source_reg2):
        self.source_reg2 = source_reg2

    def set_immediate(self, immediate):
        self.immediate = immediate

    def set_destination_reg(self, destination_reg):
        self.destination_reg = destination_reg
