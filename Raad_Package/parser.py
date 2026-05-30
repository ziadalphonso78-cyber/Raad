# parser.py - Fixed version with function call support
from tokens import *
from nodes import *
from results import ParseResult
from errors import InvalidSyntaxError

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.current_tok = None
        self.advance()
    
    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok
    
    def parse(self):
        res = self.program()
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Unexpected token"
            ))
        return res
    
    def program(self):
        res = ParseResult()
        statements = []
        
        while self.current_tok.type != TT_EOF:
            stmt = res.register(self.statement())
            if res.error: return res
            statements.append(stmt)
        
        return res.success(ProgramNode(statements))
    
    def statement(self):
        res = ParseResult()
        
        if self.current_tok.type == TT_KEYWORD:
            if self.current_tok.value == 'var':
                return self.var_assign(is_const=False)
            elif self.current_tok.value == 'const':
                return self.var_assign(is_const=True)
            elif self.current_tok.value == 'if':
                return self.if_expr()
            elif self.current_tok.value == 'while':
                return self.while_expr()
        
        # Check for expression (could be function call, variable, etc.)
        expr = res.register(self.expr())
        if res.error: return res
        
        if self.current_tok.type == TT_SEMI:
            res.register(self.advance())
        
        return res.success(expr)
    
    def expr(self):
        """Parse expressions with function calls"""
        return self.bin_op(self.comp_expr, (TT_AND, TT_OR))
    
    def comp_expr(self):
        return self.bin_op(self.arith_expr, (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE))
    
    def arith_expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))
    
    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV, TT_MOD, TT_FLOORDIV))
    
    def factor(self):
        res = ParseResult()
        tok = self.current_tok
        
        if tok.type in (TT_PLUS, TT_MINUS, TT_NOT):
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))
        
        return self.power()
    
    def power(self):
        return self.bin_op(self.atom, (TT_POW,), self.factor)
    
    def atom(self):
        res = ParseResult()
        tok = self.current_tok
        
        # Prefix increment/decrement
        if tok.type in (TT_INC, TT_DEC):
            op_tok = self.current_tok
            res.register(self.advance())
            
            if self.current_tok.type != TT_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected identifier"
                ))
            
            var_node = VarAccessNode(self.current_tok)
            res.register(self.advance())
            
            inc_node = IncrementNode(var_node, is_postfix=False, is_increment=(op_tok.type == TT_INC))
            return res.success(inc_node)
        
        # Numbers
        if tok.type in (TT_INT, TT_FLOAT):
            res.register(self.advance())
            node = NumberNode(tok)
            return res.success(self.parse_function_calls(node))
        
        # Strings
        elif tok.type == TT_STRING:
            res.register(self.advance())
            node = StringNode(tok)
            return res.success(self.parse_function_calls(node))
        
        # Identifiers (could be variable or function name)
        elif tok.type == TT_IDENTIFIER:
            var_tok = self.current_tok
            res.register(self.advance())
            
            # Check for function call
            if self.current_tok and self.current_tok.type == TT_LPAREN:
                return self.function_call(var_tok)
            
            # Check for assignment
            if self.current_tok and self.current_tok.type in (TT_PLUSEQ, TT_MINUSEQ, TT_MULEQ, 
                                                               TT_DIVEQ, TT_POWEQ, TT_FLOORDIVEQ, TT_MODEQ):
                return self.var_assign_op(var_tok)
            elif self.current_tok and self.current_tok.type == TT_EQ:
                return self.var_set(var_tok)
            
            # Variable access
            node = VarAccessNode(var_tok)
            return res.success(self.parse_postfix(self.parse_function_calls(node)))
        
        # Parentheses
        elif tok.type == TT_LPAREN:
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_tok.type == TT_RPAREN:
                res.register(self.advance())
                return res.success(self.parse_function_calls(expr))
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected ')'"
            ))
        
        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            "Expected number, string, identifier, or '('"
        ))
    
    def function_call(self, func_name_tok):
        """Parse function calls like print("Hello")"""
        res = ParseResult()
        pos_start = func_name_tok.pos_start
        
        res.register(self.advance())  # Consume '('
        
        # Parse arguments
        args = []
        
        if self.current_tok.type != TT_RPAREN:
            while True:
                arg = res.register(self.expr())
                if res.error: return res
                args.append(arg)
                
                if self.current_tok.type == TT_COMMA:
                    res.register(self.advance())
                else:
                    break
        
        if self.current_tok.type != TT_RPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected ')' after arguments"
            ))
        
        res.register(self.advance())  # Consume ')'
        
        # Create function call node
        func_node = VarAccessNode(func_name_tok)
        call_node = FunctionCallNode(func_node, args, pos_start, self.current_tok.pos_end if self.current_tok else pos_start)
        
        # Check for method calls after function call
        return res.success(self.parse_method_calls(call_node))
    
    def parse_function_calls(self, node):
        """Parse chained function calls"""
        res = ParseResult()
        
        while self.current_tok and self.current_tok.type == TT_LPAREN:
            pos_start = node.pos_start
            
            res.register(self.advance())  # Consume '('
            
            # Parse arguments
            args = []
            if self.current_tok.type != TT_RPAREN:
                while True:
                    arg = res.register(self.expr())
                    if res.error: return res
                    args.append(arg)
                    
                    if self.current_tok.type == TT_COMMA:
                        res.register(self.advance())
                    else:
                        break
            
            if self.current_tok.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')'"
                ))
            
            res.register(self.advance())  # Consume ')'
            node = FunctionCallNode(node, args, pos_start, self.current_tok.pos_end if self.current_tok else pos_start)
        
        return res.success(node)
    
    def parse_method_calls(self, node):
        """Parse method calls like obj.method()"""
        res = ParseResult()
        
        while self.current_tok and self.current_tok.type == TT_DOT:
            res.register(self.advance())  # Consume '.'
            
            if self.current_tok.type != TT_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected method name"
                ))
            
            method_name = self.current_tok.value
            res.register(self.advance())
            
            if self.current_tok.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '(' after method name"
                ))
            
            res.register(self.advance())  # Consume '('
            
            # Parse arguments
            args = []
            if self.current_tok.type != TT_RPAREN:
                while True:
                    arg = res.register(self.expr())
                    if res.error: return res
                    args.append(arg)
                    
                    if self.current_tok.type == TT_COMMA:
                        res.register(self.advance())
                    else:
                        break
            
            if self.current_tok.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')'"
                ))
            
            res.register(self.advance())  # Consume ')'
            node = MethodCallNode(node, method_name, args, node.pos_start, self.current_tok.pos_end if self.current_tok else node.pos_end)
        
        return res.success(node)
    
    def parse_postfix(self, node):
        """Parse postfix increment/decrement (x++, x--)"""
        res = ParseResult()
        
        if self.current_tok and self.current_tok.type in (TT_INC, TT_DEC):
            op_tok = self.current_tok
            res.register(self.advance())
            
            if isinstance(node, VarAccessNode):
                inc_node = IncrementNode(node, is_postfix=True, is_increment=(op_tok.type == TT_INC))
                return res.success(inc_node)
        
        return res.success(node)
    
    def var_assign(self, is_const):
        res = ParseResult()
        res.register(self.advance())  # consume var/const
        
        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected identifier"
            ))
        
        var_tok = self.current_tok
        res.register(self.advance())
        
        type_annotation = None
        if self.current_tok.type == TT_COLON:
            res.register(self.advance())
            if self.current_tok.type not in [
                'int', 'float', 'string', 'boolean', 'list', 'char', 'any'
            ]:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected type annotation (int, float, string, boolean, list, char, any) after ':'"
                ))
            type_annotation = self.current_tok
            res.register(self.advance())

        if self.current_tok.type != TT_EQ:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '='"
            ))
        
        res.register(self.advance())
        expr = res.register(self.expr())
        if res.error: return res
        
        if self.current_tok.type == TT_SEMI:
            res.register(self.advance())
        
        return res.success(VarAssignNode(var_tok, expr, is_const, type_annotation))
    
    def var_set(self, var_tok):
        res = ParseResult()
        res.register(self.advance())  # consume '='
        
        expr = res.register(self.expr())
        if res.error: return res
        
        return res.success(VarSetNode(var_tok, expr))
    
    def var_assign_op(self, var_tok):
        res = ParseResult()
        op_tok = self.current_tok
        res.register(self.advance())  # consume operator
        
        expr = res.register(self.expr())
        if res.error: return res
        
        return res.success(VarAssignOpNode(var_tok, op_tok, expr))
    
    def if_expr(self):
        res = ParseResult()
        cases = []
        else_case = None
        
        res.register(self.advance())  # consume 'if'
        condition = res.register(self.expr())
        if res.error: return res
        
        if self.current_tok.type != TT_LCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '{'"
            ))
        
        res.register(self.advance())  # consume '{'
        body = res.register(self.statement())
        if res.error: return res
        
        if self.current_tok.type == TT_RCURLY:
            res.register(self.advance())  # consume '}'
        else:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '}'"
            ))
        
        cases.append((condition, body))
        
        while self.current_tok.type == TT_KEYWORD and self.current_tok.value == 'elif':
            res.register(self.advance())
            condition = res.register(self.expr())
            if res.error: return res
            
            if self.current_tok.type != TT_LCURLY:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '{'"
                ))
            
            res.register(self.advance())
            body = res.register(self.statement())
            if res.error: return res
            
            if self.current_tok.type == TT_RCURLY:
                res.register(self.advance())
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '}'"
                ))
            
            cases.append((condition, body))
        
        if self.current_tok.type == TT_KEYWORD and self.current_tok.value == 'else':
            res.register(self.advance())
            
            if self.current_tok.type != TT_LCURLY:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '{'"
                ))
            
            res.register(self.advance())
            else_case = res.register(self.statement())
            if res.error: return res
            
            if self.current_tok.type == TT_RCURLY:
                res.register(self.advance())
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '}'"
                ))
        
        return res.success(IfNode(cases, else_case))
    
    def while_expr(self):
        res = ParseResult()
        res.register(self.advance())  # consume 'while'
        
        condition = res.register(self.expr())
        if res.error: return res
        
        if self.current_tok.type != TT_LCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '{'"
            ))
        
        res.register(self.advance())
        body = res.register(self.statement())
        if res.error: return res
        
        if self.current_tok.type == TT_RCURLY:
            res.register(self.advance())
        else:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '}'"
            ))
        
        return res.success(WhileNode(condition, body))
    
    def bin_op(self, func_a, ops, func_b=None):
        if func_b is None:
            func_b = func_a
        
        res = ParseResult()
        left = res.register(func_a())
        if res.error: return res
        
        while self.current_tok and self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(func_b())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)
        
        return res.success(left)