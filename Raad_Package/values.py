# values.py
from errors import RTError

class Value:
    def __init__(self, value):
        self.value = value
        self.set_pos()
        self.set_context()
    
    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def set_context(self, context=None):
        self.context = context
        return self
    
    def added_to(self, other):
        return None, self.illegal_operation(other)
    
    def subbed_by(self, other):
        return None, self.illegal_operation(other)
    
    def multed_by(self, other):
        return None, self.illegal_operation(other)
    
    def dived_by(self, other):
        return None, self.illegal_operation(other)
    
    def powed_by(self, other):
        return None, self.illegal_operation(other)
    
    def floordived_by(self, other):
        return None, self.illegal_operation(other)
    
    def modded_by(self, other):
        return None, self.illegal_operation(other)
    
    def get_comparison_eq(self, other):
        return None, self.illegal_operation(other)
    
    def get_comparison_ne(self, other):
        return None, self.illegal_operation(other)
    
    def get_comparison_lt(self, other):
        return None, self.illegal_operation(other)
    
    def get_comparison_gt(self, other):
        return None, self.illegal_operation(other)
    
    def get_comparison_lte(self, other):
        return None, self.illegal_operation(other)
    
    def get_comparison_gte(self, other):
        return None, self.illegal_operation(other)
    
    def anded_by(self, other):
        return None, self.illegal_operation(other)
    
    def ored_by(self, other):
        return None, self.illegal_operation(other)
    
    def notted(self):
        return None, self.illegal_operation(other=None)
    
    def illegal_operation(self, other=None):
        if other:
            return RTError(
                self.pos_start, other.pos_end,
                f"Illegal operation: {self} {self.get_operation_name()} {other}",
                self.context
            )
        return RTError(
            self.pos_start, self.pos_end,
            f"Illegal operation on {self}",
            self.context
        )
    
    def get_operation_name(self):
        return "operation"
    
    def is_true(self):
        return bool(self.value)
    
    def __repr__(self):
        return str(self.value)

class Number(Value):
    def __init__(self, value):
        super().__init__(value)
    
    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value), None
        elif isinstance(other, String):
            return String(str(self.value) + other.value), None
        return None, self.illegal_operation(other)
    
    def subbed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value), None
        return None, self.illegal_operation(other)
    
    def multed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value), None
        elif isinstance(other, String):
            if self.value < 0:
                return None, RTError(
                    self.pos_start, other.pos_end,
                    "Cannot multiply string by negative number",
                    self.context
                )
            return String(other.value * int(self.value)), None
        return None, self.illegal_operation(other)
    
    def dived_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    self.pos_start, other.pos_end,
                    "Division by zero",
                    self.context
                )
            return Number(self.value / other.value), None
        return None, self.illegal_operation(other)
    
    def powed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value), None
        return None, self.illegal_operation(other)
    
    def floordived_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    self.pos_start, other.pos_end,
                    "Division by zero",
                    self.context
                )
            return Number(self.value // other.value), None
        return None, self.illegal_operation(other)
    
    def modded_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    self.pos_start, other.pos_end,
                    "Modulo by zero",
                    self.context
                )
            return Number(self.value % other.value), None
        return None, self.illegal_operation(other)
    
    def get_comparison_eq(self, other):
        if isinstance(other, Number):
            return Number(1 if self.value == other.value else 0), None
        return Number(0), None
    
    def get_comparison_ne(self, other):
        if isinstance(other, Number):
            return Number(1 if self.value != other.value else 0), None
        return Number(1), None
    
    def get_comparison_lt(self, other):
        if isinstance(other, Number):
            return Number(1 if self.value < other.value else 0), None
        return None, self.illegal_operation(other)
    
    def get_comparison_gt(self, other):
        if isinstance(other, Number):
            return Number(1 if self.value > other.value else 0), None
        return None, self.illegal_operation(other)
    
    def get_comparison_lte(self, other):
        if isinstance(other, Number):
            return Number(1 if self.value <= other.value else 0), None
        return None, self.illegal_operation(other)
    
    def get_comparison_gte(self, other):
        if isinstance(other, Number):
            return Number(1 if self.value >= other.value else 0), None
        return None, self.illegal_operation(other)
    
    def anded_by(self, other):
        if isinstance(other, Number):
            return Number(1 if (self.value and other.value) else 0), None
        return None, self.illegal_operation(other)
    
    def ored_by(self, other):
        if isinstance(other, Number):
            return Number(1 if (self.value or other.value) else 0), None
        return None, self.illegal_operation(other)
    
    def notted(self):
        return Number(1 if self.value == 0 else 0), None
    
    def get_operation_name(self):
        return "number"
    
    def __repr__(self):
        return str(self.value)

class String(Value):
    def __init__(self, value):
        super().__init__(value)
    
    def added_to(self, other):
        if isinstance(other, (String, Number)):
            return String(self.value + str(other.value)), None
        return None, self.illegal_operation(other)
    
    def multed_by(self, other):
        if isinstance(other, Number):
            if other.value < 0:
                return None, RTError(
                    self.pos_start, other.pos_end,
                    "Cannot multiply string by negative number",
                    self.context
                )
            return String(self.value * int(other.value)), None
        return None, self.illegal_operation(other)
    
    def subbed_by(self, other):
        if isinstance(other, String):
            return String(self.value.replace(other.value, "", 1)), None
        return None, self.illegal_operation(other)
    
    def dived_by(self, other):
        if isinstance(other, String):
            return String(self.value.split(other.value)), None
        return None, self.illegal_operation(other)

    def get_comparison_eq(self, other):
        if isinstance(other, String):
            return Number(1 if self.value == other.value else 0), None
        return Number(0), None
    
    def get_comparison_ne(self, other):
        if isinstance(other, String):
            return Number(1 if self.value != other.value else 0), None
        return Number(1), None
    
    def method_length(self):
        return Number(len(self.value)), None
    
    def method_upper(self):
        return String(self.value.upper()), None
    
    def method_lower(self):
        return String(self.value.lower()), None
    
    def get_methods(self):
        return {
            "len": self.method_length,
            "length": self.method_length,
            "upper": self.method_upper,
            "lower": self.method_lower,
        }
    
    def get_operation_name(self):
        return "string"
    
    def __repr__(self):
        return f"{self.value}"
    
    def is_true(self):
        return len(self.value) > 0

class List(Value):
    def __init__(self, elements):
        super().__init__(elements)
        self.elements = elements
    
    def method_length(self):
        return Number(len(self.elements)), None
    
    def method_append(self, element):
        self.elements.append(element)
        return self, None
    
    def get_methods(self):
        return {
            "len": self.method_length,
            "length": self.method_length,
            "append": self.method_append,
        }
    
    def __repr__(self):
        return f"[{', '.join(str(elem) for elem in self.elements)}]"

class Boolean(Number):
    def __init__(self, value):
        super().__init__(1 if value else 0)
    
    def __repr__(self):
        return "true" if self.value else "false"

class Null(Value):
    def __init__(self):
        super().__init__(None)
    
    def __repr__(self):
        return "null"
    
    def is_true(self):
        return False

# values.py - Fix BuiltInFunction to handle variable arguments

class BuiltInFunction(Value):
    def __init__(self, name, func, arg_count=0):
        super().__init__(name)
        self.name = name
        self.func = func
        self.arg_count = arg_count  # -1 means variable number of arguments
    
    def execute(self, args):
        # Check argument count (skip if arg_count is -1 = variable args)
        if self.arg_count != -1 and len(args) != self.arg_count:
            return None, RTError(
                self.pos_start, self.pos_end,
                f"Expected {self.arg_count} arguments, got {len(args)}",
                self.context
            )
        
        try:
            result = self.func(args, self.context)
            return result, None
        except Exception as e:
            return None, RTError(
                self.pos_start, self.pos_end,
                f"Error in built-in function '{self.name}': {str(e)}",
                self.context
            )
    
    def __repr__(self):
        return f"<built-in function {self.name}>"