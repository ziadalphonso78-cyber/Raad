# nodes.py
class NumberNode:
    def __init__(self, tok):
        self.tok = tok
        self.value = tok.value
        self.pos_start = tok.pos_start
        self.pos_end = tok.pos_end
    
    def __repr__(self):
        return f"{self.value}"

class StringNode:
    def __init__(self, tok):
        self.tok = tok
        self.value = tok.value
        self.pos_start = tok.pos_start
        self.pos_end = tok.pos_end
    
    def __repr__(self):
        return f'"{self.value}"'

class VarAccessNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok
        self.var_name = var_name_tok.value
        self.pos_start = var_name_tok.pos_start
        self.pos_end = var_name_tok.pos_end
    
    def __repr__(self):
        return f"VarAccess({self.var_name})"

class VarAssignNode:
    def __init__(self, var_name_tok, value_node, is_const=False, type_annotation=None):
        self.var_name_tok = var_name_tok
        self.var_name = var_name_tok.value
        self.value_node = value_node
        self.is_const = is_const
        self.type_annotation = type_annotation
        self.pos_start = var_name_tok.pos_start
        self.pos_end = value_node.pos_end if hasattr(value_node, 'pos_end') else var_name_tok.pos_end
    
    def __repr__(self):
        return f"VarAssign({self.var_name}, const={self.is_const})"

class VarSetNode:
    def __init__(self, var_name_tok, value_node):
        self.var_name_tok = var_name_tok
        self.var_name = var_name_tok.value
        self.value_node = value_node
        self.pos_start = var_name_tok.pos_start
        self.pos_end = value_node.pos_end if hasattr(value_node, 'pos_end') else var_name_tok.pos_end
    
    def __repr__(self):
        return f"VarSet({self.var_name})"

class VarAssignOpNode:
    def __init__(self, var_name_tok, op_tok, value_node):
        self.var_name_tok = var_name_tok
        self.var_name = var_name_tok.value
        self.op_tok = op_tok
        self.value_node = value_node
        self.pos_start = var_name_tok.pos_start
        self.pos_end = value_node.pos_end if hasattr(value_node, 'pos_end') else op_tok.pos_end
    
    def __repr__(self):
        return f"VarAssignOp({self.var_name} {self.op_tok.type} {self.value_node})"

class IncrementNode:
    def __init__(self, var_node, is_postfix=False, is_increment=True):
        self.var_node = var_node
        self.var_name = var_node.var_name
        self.is_postfix = is_postfix
        self.is_increment = is_increment
        self.pos_start = var_node.pos_start
        self.pos_end = var_node.pos_end
    
    def __repr__(self):
        op = "++" if self.is_increment else "--"
        if self.is_postfix:
            return f"Post{op}({self.var_name})"
        return f"Pre{op}({self.var_name})"

class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node
        self.pos_start = left_node.pos_start if hasattr(left_node, 'pos_start') else op_tok.pos_start
        self.pos_end = right_node.pos_end if hasattr(right_node, 'pos_end') else op_tok.pos_end
    
    def __repr__(self):
        return f"({self.left_node} {self.op_tok.type} {self.right_node})"

class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node
        self.pos_start = op_tok.pos_start
        self.pos_end = node.pos_end if hasattr(node, 'pos_end') else op_tok.pos_end
    
    def __repr__(self):
        return f"({self.op_tok.type} {self.node})"

class IfNode:
    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_case = else_case
        self.pos_start = cases[0][0].pos_start
        if else_case:
            self.pos_end = else_case.pos_end
        else:
            self.pos_end = cases[-1][0].pos_end

class WhileNode:
    def __init__(self, condition_node, body_node):
        self.condition_node = condition_node
        self.body_node = body_node
        self.pos_start = condition_node.pos_start
        self.pos_end = body_node.pos_end if hasattr(body_node, 'pos_end') else condition_node.pos_end

class FunctionCallNode:
    def __init__(self, func_node, args, pos_start, pos_end):
        self.func_node = func_node
        self.args = args
        self.pos_start = pos_start
        self.pos_end = pos_end
    
    def __repr__(self):
        return f"{self.func_node}({', '.join(str(a) for a in self.args)})"

class MethodCallNode:
    def __init__(self, obj_node, method_name, args, pos_start, pos_end):
        self.obj_node = obj_node
        self.method_name = method_name
        self.args = args
        self.pos_start = pos_start
        self.pos_end = pos_end
    
    def __repr__(self):
        return f"{self.obj_node}.{self.method_name}({', '.join(str(a) for a in self.args)})"

class ProgramNode:
    def __init__(self, statements):
        self.statements = statements
        if statements:
            self.pos_start = statements[0].pos_start if hasattr(statements[0], 'pos_start') else None
            self.pos_end = statements[-1].pos_end if hasattr(statements[-1], 'pos_end') else None
        else:
            self.pos_start = None
            self.pos_end = None