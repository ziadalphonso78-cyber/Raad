# interpreter.py

from nodes import *
from values import Number, String, List, Boolean, Null, BuiltInFunction
from results import RTResult
from errors import RTError
from tokens import *

class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)
    
    def no_visit_method(self, node, context):
        raise Exception(f"No visit_{type(node).__name__} method defined")
    
    def visit_NumberNode(self, node, context):
        return RTResult().success(
            Number(node.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
    
    def visit_StringNode(self, node, context):
        return RTResult().success(
            String(node.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
    
    def visit_VarAccessNode(self, node, context):
        res = RTResult()
        var_name = node.var_name
        value = context.symbol_table.get(var_name)
        
        if value is None:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f"Variable '{var_name}' is not defined",
                context
            ))
        
        return res.success(value)
    
    def check_type(self, value, expected_type, pos_start, pos_end, context):
        if expected_type or expected_type == 'any':
            return True, None
        
        type_mapping = {
            'int': Number,
            'float': Number,
            'string': String,
            'boolean': Boolean,
            'list': List,
        }

    def visit_VarAssignNode(self, node, context):
        res = RTResult()
        var_name = node.var_name
        
        if context.symbol_table.get(var_name) is not None:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f"Variable '{var_name}' is already defined",
                context
            ))
        
        value = res.register(self.visit(node.value_node, context))
        if res.error: return res
        
        context.symbol_table.set(var_name, value, node.is_const)
        return res.success(value)
    
    def visit_VarSetNode(self, node, context):
        res = RTResult()
        var_name = node.var_name
        
        if context.symbol_table.get(var_name) is None:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f"Variable '{var_name}' is not defined",
                context
            ))
        
        if context.symbol_table.is_constant(var_name):
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f"Cannot reassign constant variable '{var_name}'",
                context
            ))
        
        value = res.register(self.visit(node.value_node, context))
        if res.error: return res
        
        context.symbol_table.set(var_name, value, False)
        return res.success(value)
    
    def visit_VarAssignOpNode(self, node, context):
        res = RTResult()
        var_name = node.var_name
        
        if context.symbol_table.get(var_name) is None:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f"Variable '{var_name}' is not defined",
                context
            ))
        
        if context.symbol_table.is_constant(var_name):
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f"Cannot reassign constant variable '{var_name}'",
                context
            ))
        
        current = context.symbol_table.get(var_name)
        new_value = res.register(self.visit(node.value_node, context))
        if res.error: return res
        
        op_type = node.op_tok.type
        
        if op_type == TT_PLUSEQ:
            result, error = current.added_to(new_value)
        elif op_type == TT_MINUSEQ:
            result, error = current.subbed_by(new_value)
        elif op_type == TT_MULEQ:
            result, error = current.multed_by(new_value)
        elif op_type == TT_DIVEQ:
            result, error = current.dived_by(new_value)
        elif op_type == TT_POWEQ:
            result, error = current.powed_by(new_value)
        elif op_type == TT_FLOORDIVEQ:
            result, error = current.floordived_by(new_value)
        elif op_type == TT_MODEQ:
            result, error = current.modded_by(new_value)
        else:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f"Unknown compound operator",
                context
            ))
        
        if error:
            return res.failure(error)
        
        context.symbol_table.set(var_name, result, False)
        return res.success(result)
    
    def visit_IncrementNode(self, node, context):
        res = RTResult()
        var_name = node.var_name
        
        if context.symbol_table.get(var_name) is None:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f"Variable '{var_name}' is not defined",
                context
            ))
        
        if context.symbol_table.is_constant(var_name):
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f"Cannot increment/decrement constant variable '{var_name}'",
                context
            ))
        
        current = context.symbol_table.get(var_name)
        
        if not isinstance(current, Number):
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f"Cannot increment/decrement non-number value",
                context
            ))
        
        increment = 1 if node.is_increment else -1
        new_value, error = current.added_to(Number(increment))
        
        if error:
            return res.failure(error)
        
        if node.is_postfix:
            result = current
        else:
            result = new_value
        
        context.symbol_table.set(var_name, new_value, False)
        return res.success(result)
    
    def visit_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.error: return res
        right = res.register(self.visit(node.right_node, context))
        if res.error: return res
        
        if node.op_tok.type == TT_PLUS:
            result, error = left.added_to(right)
        elif node.op_tok.type == TT_MINUS:
            result, error = left.subbed_by(right)
        elif node.op_tok.type == TT_MUL:
            result, error = left.multed_by(right)
        elif node.op_tok.type == TT_DIV:
            result, error = left.dived_by(right)
        elif node.op_tok.type == TT_POW:
            result, error = left.powed_by(right)
        elif node.op_tok.type == TT_FLOORDIV:
            result, error = left.floordived_by(right)
        elif node.op_tok.type == TT_MOD:
            result, error = left.modded_by(right)
        elif node.op_tok.type == TT_EE:
            result, error = left.get_comparison_eq(right)
        elif node.op_tok.type == TT_NE:
            result, error = left.get_comparison_ne(right)
        elif node.op_tok.type == TT_LT:
            result, error = left.get_comparison_lt(right)
        elif node.op_tok.type == TT_GT:
            result, error = left.get_comparison_gt(right)
        elif node.op_tok.type == TT_LTE:
            result, error = left.get_comparison_lte(right)
        elif node.op_tok.type == TT_GTE:
            result, error = left.get_comparison_gte(right)
        elif node.op_tok.type == TT_AND:
            result, error = left.anded_by(right)
        elif node.op_tok.type == TT_OR:
            result, error = left.ored_by(right)
        else:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f"Unknown operator",
                context
            ))
        
        if error:
            return res.failure(error)
        return res.success(result.set_pos(node.pos_start, node.pos_end))
    
    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.error: return res
        
        if node.op_tok.type == TT_MINUS:
            number, error = number.multed_by(Number(-1))
        elif node.op_tok.type == TT_NOT:
            number, error = number.notted()
        else:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f"Unknown unary operator",
                context
            ))
        
        if error:
            return res.failure(error)
        return res.success(number)
    
    def visit_IfNode(self, node, context):
        res = RTResult()
        
        for condition, expr in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.error: return res
            
            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.error: return res
                return res.success(expr_value)
        
        if node.else_case:
            else_value = res.register(self.visit(node.else_case, context))
            if res.error: return res
            return res.success(else_value)
        
        return res.success(Null())
    
    def visit_WhileNode(self, node, context):
        res = RTResult()
        
        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.error: return res
            
            if not condition.is_true():
                break
            
            body = res.register(self.visit(node.body_node, context))
            if res.error: return res
        
        return res.success(Null())
    
    
    def visit_FunctionCallNode(self, node, context):
        """Handle function calls like print(), input(), etc."""
        res = RTResult()
        
        # Evaluate the function (should be a BuiltInFunction or variable)
        func = res.register(self.visit(node.func_node, context))
        if res.error: return res
        
        # Evaluate arguments
        args = []
        for arg_node in node.args:
            arg = res.register(self.visit(arg_node, context))
            if res.error: return res
            args.append(arg)
        
        # Check if it's a built-in function
        if isinstance(func, BuiltInFunction):
            result, error = func.execute(args)
            if error:
                return res.failure(error)
            return res.success(result)
        
        # Check if it's a user-defined function (if you have them)
        elif hasattr(func, 'execute'):
            result, error = func.execute(args)
            if error:
                return res.failure(error)
            return res.success(result)
        
        else:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f"'{func}' is not a function",
                context
            ))
    
    def visit_ProgramNode(self, node, context):
        res = RTResult()
        last_value = Null()
        
        for stmt in node.statements:
            last_value = res.register(self.visit(stmt, context))
            if res.error: return res
        
        return res.success(last_value)

    def visit_ParseResult(self, node, context):
        """Handle ParseResult objects by extracting the value"""
        # ParseResult objects have a .value attribute that contains the actual AST node
        if node and hasattr(node, 'value'):
            return self.visit(node.value, context)
        return RTResult().success(Null())