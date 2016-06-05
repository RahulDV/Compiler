# This file contains the class Token. It is used to encapsulate the type and value of a identified token.
#

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def getValue(self):
        return self.value

    def getType(self):
        return self.type

    def setType(self, type):
        self.type = type
