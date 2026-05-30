class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.types = {}
        self.constants = set()
        self.parent = parent
    
    def get(self, name):
        value = self.symbols.get(name, None)
        if value is None and self.parent:
            return self.parent.get(name)
        return value
    
    def set(self, name, value, is_const=False):
        self.symbols[name] = value
        if is_const:
            self.constants.add(name)
        return True
    
    def remove(self, name):
        del self.symbols[name]
    
    def is_constant(self, name):
        if name in self.constants:
            return True
        if self.parent:
            return self.parent.is_constant(name)
        return False
