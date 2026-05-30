# lexer.py - Fixed version with better comment handling
from tokens import *
from errors import IllegalCharError

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt
    
    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1
        
        if current_char == '\n':
            self.ln += 1
            self.col = 0
        
        return self
    
    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()
    
    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None
    
    def peek(self):
        """Look at the next character without advancing"""
        if self.pos.idx + 1 < len(self.text):
            return self.text[self.pos.idx + 1]
        return None
    
    def skip_comment(self):
        """Skip single-line comment starting with #"""
        self.advance()  # Skip the #
        while self.current_char is not None and self.current_char != '\n':
            self.advance()
    
    def skip_multi_comment(self):
        """Skip multi-line comment between /- and -/"""
        self.advance()  # Skip /
        if self.current_char == '-':
            self.advance()  # Skip -
        else:
            return
        
        while self.current_char is not None:
            if self.current_char == '-' and self.peek() == '/':
                self.advance()  # Skip -
                if self.current_char == '/':
                    self.advance()  # Skip /
                break
            self.advance()
    
    def make_tokens(self):
        tokens = []
        
        while self.current_char is not None:
            # Skip whitespace
            if self.current_char in ' \t\n':
                self.advance()
            
            # Single-line comment
            elif self.current_char == '#':
                self.skip_comment()
            
            # Multi-line comment start (only when not inside a string)
            elif self.current_char == '/' and self.peek() == '-':
                self.skip_multi_comment()
            
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())
            
            elif self.current_char == '"':
                tokens.append(self.make_string())
            
            # Operators and symbols
            elif self.current_char == '+':
                pos_start = self.pos.copy()
                self.advance()
                if self.current_char == '+':
                    self.advance()
                    tokens.append(Token(TT_INC, pos_start=pos_start, pos_end=self.pos.copy()))
                elif self.current_char == '=':
                    self.advance()
                    tokens.append(Token(TT_PLUSEQ, pos_start=pos_start, pos_end=self.pos.copy()))
                else:
                    tokens.append(Token(TT_PLUS, pos_start=pos_start, pos_end=self.pos.copy()))
            
            elif self.current_char == '-':
                pos_start = self.pos.copy()
                self.advance()
                if self.current_char == '-':
                    self.advance()
                    tokens.append(Token(TT_DEC, pos_start=pos_start, pos_end=self.pos.copy()))
                elif self.current_char == '=':
                    self.advance()
                    tokens.append(Token(TT_MINUSEQ, pos_start=pos_start, pos_end=self.pos.copy()))
                else:
                    tokens.append(Token(TT_MINUS, pos_start=pos_start, pos_end=self.pos.copy()))
            
            elif self.current_char == '*':
                pos_start = self.pos.copy()
                self.advance()
                if self.current_char == '*':
                    self.advance()
                    if self.current_char == '=':
                        self.advance()
                        tokens.append(Token(TT_POWEQ, pos_start=pos_start, pos_end=self.pos.copy()))
                    else:
                        tokens.append(Token(TT_POW, pos_start=pos_start, pos_end=self.pos.copy()))
                elif self.current_char == '=':
                    self.advance()
                    tokens.append(Token(TT_MULEQ, pos_start=pos_start, pos_end=self.pos.copy()))
                else:
                    tokens.append(Token(TT_MUL, pos_start=pos_start, pos_end=self.pos.copy()))
            
            elif self.current_char == '/':
                # Check for multi-line comment start
                if self.peek() == '-':
                    self.skip_multi_comment()
                else:
                    pos_start = self.pos.copy()
                    self.advance()
                    if self.current_char == '/':
                        self.advance()
                        if self.current_char == '=':
                            self.advance()
                            tokens.append(Token(TT_FLOORDIVEQ, pos_start=pos_start, pos_end=self.pos.copy()))
                        else:
                            tokens.append(Token(TT_FLOORDIV, pos_start=pos_start, pos_end=self.pos.copy()))
                    elif self.current_char == '=':
                        self.advance()
                        tokens.append(Token(TT_DIVEQ, pos_start=pos_start, pos_end=self.pos.copy()))
                    else:
                        tokens.append(Token(TT_DIV, pos_start=pos_start, pos_end=self.pos.copy()))
            
            elif self.current_char == '%':
                pos_start = self.pos.copy()
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    tokens.append(Token(TT_MODEQ, pos_start=pos_start, pos_end=self.pos.copy()))
                else:
                    tokens.append(Token(TT_MOD, pos_start=pos_start, pos_end=self.pos.copy()))
            
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start=self.pos.copy()))
                self.advance()
            
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.pos.copy()))
                self.advance()
            
            elif self.current_char == '{':
                tokens.append(Token(TT_LCURLY, pos_start=self.pos.copy()))
                self.advance()
            
            elif self.current_char == '}':
                tokens.append(Token(TT_RCURLY, pos_start=self.pos.copy()))
                self.advance()
            
            elif self.current_char == '[':
                tokens.append(Token(TT_LSQUARE, pos_start=self.pos.copy()))
                self.advance()
            
            elif self.current_char == ']':
                tokens.append(Token(TT_RSQUARE, pos_start=self.pos.copy()))
                self.advance()
            
            elif self.current_char == ';':
                tokens.append(Token(TT_SEMI, pos_start=self.pos.copy()))
                self.advance()
            
            elif self.current_char == ':':
                tokens.append(Token(TT_COLON, pos_start=self.pos.copy()))
                self.advance()
            
            elif self.current_char == ',':
                tokens.append(Token(TT_COMMA, pos_start=self.pos.copy()))
                self.advance()
            
            elif self.current_char == '.':
                tokens.append(Token(TT_DOT, pos_start=self.pos.copy()))
                self.advance()
            
            elif self.current_char == '=':
                pos_start = self.pos.copy()
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    tokens.append(Token(TT_EE, pos_start=pos_start, pos_end=self.pos.copy()))
                else:
                    tokens.append(Token(TT_EQ, pos_start=pos_start, pos_end=self.pos.copy()))
            
            elif self.current_char == '!':
                pos_start = self.pos.copy()
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    tokens.append(Token(TT_NE, pos_start=pos_start, pos_end=self.pos.copy()))
                else:
                    tokens.append(Token(TT_NOT, pos_start=pos_start, pos_end=self.pos.copy()))
            
            elif self.current_char == '<':
                pos_start = self.pos.copy()
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    tokens.append(Token(TT_LTE, pos_start=pos_start, pos_end=self.pos.copy()))
                else:
                    tokens.append(Token(TT_LT, pos_start=pos_start, pos_end=self.pos.copy()))
            
            elif self.current_char == '>':
                pos_start = self.pos.copy()
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    tokens.append(Token(TT_GTE, pos_start=pos_start, pos_end=self.pos.copy()))
                else:
                    tokens.append(Token(TT_GT, pos_start=pos_start, pos_end=self.pos.copy()))
            
            elif self.current_char == '&':
                self.advance()
                if self.current_char == '&':
                    self.advance()
                    tokens.append(Token(TT_AND, pos_start=self.pos.copy()))
                else:
                    return [], IllegalCharError(self.pos.copy(), self.pos.copy(), "Expected '&'")
            
            elif self.current_char == '|':
                self.advance()
                if self.current_char == '|':
                    self.advance()
                    tokens.append(Token(TT_OR, pos_start=self.pos.copy()))
                else:
                    return [], IllegalCharError(self.pos.copy(), self.pos.copy(), "Expected '|'")
            
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos.copy(), f"'{char}'")
        
        # Add EOF token
        eof_pos = self.pos.copy()
        tokens.append(Token(TT_EOF, pos_start=eof_pos))
        return tokens, None
    
    def make_number(self):
        num_str = ""
        dot_count = 0
        pos_start = self.pos.copy()
        
        while self.current_char is not None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: 
                    break
                dot_count += 1
            num_str += self.current_char
            self.advance()
        
        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start, self.pos.copy())
        else:
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos.copy())
    
    def make_string(self):
        string_str = ""
        pos_start = self.pos.copy()
        self.advance()  # Skip opening quote
        
        while self.current_char is not None and self.current_char != '"':
            if self.current_char == '\\':
                self.advance()
                if self.current_char == 'n':
                    string_str += '\n'
                elif self.current_char == 't':
                    string_str += '\t'
                elif self.current_char == '"':
                    string_str += '"'
                elif self.current_char == '\\':
                    string_str += '\\'
                else:
                    string_str += self.current_char
            else:
                string_str += self.current_char
            self.advance()
        
        if self.current_char == '"':
            self.advance()  # Skip closing quote
        
        return Token(TT_STRING, string_str, pos_start, self.pos.copy())
    
    def make_identifier(self):
        id_str = ""
        pos_start = self.pos.copy()
        
        while self.current_char is not None and self.current_char in LETTERS_DIGITS + '_':
            id_str += self.current_char
            self.advance()
        
        tok_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
        return Token(tok_type, id_str, pos_start, self.pos.copy())