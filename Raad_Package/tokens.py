# tokens.py
from string import ascii_letters, digits

LETTERS = ascii_letters + "_"
DIGITS = digits
LETTERS_DIGITS = LETTERS + DIGITS

# Basic tokens
TT_INT = "INT"
TT_FLOAT = "FLOAT"
TT_STRING = "STRING"
TT_CHAR = "CHAR"

# Operators
TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_MUL = "MUL"
TT_DIV = "DIV"
TT_POW = "POW"
TT_FLOORDIV = "FLOORDIV"
TT_MOD = "MOD"

# Assignment operators
TT_EQ = "EQ"
TT_PLUSEQ = "PLUSEQ"
TT_MINUSEQ = "MINUSEQ"
TT_MULEQ = "MULEQ"
TT_DIVEQ = "DIVEQ"
TT_POWEQ = "POWEQ"
TT_FLOORDIVEQ = "FLOORDIVEQ"
TT_MODEQ = "MODEQ"

# Increment/Decrement
TT_INC = "INC"
TT_DEC = "DEC"

# Type Annotations
TT_TYPE_INT = "TYPE_INT"
TT_TYPE_FLOAT = "TYPE_FLOAT"
TT_TYPE_STRING = "TYPE_STRING"
TT_TYPE_BOOLEAN = "TYPE_BOOLEAN"
TT_TYPE_NULL = "TYPE_NULL"
TT_TYPE_LIST = "TYPE_LIST"
TT_TYPE_ANY = "TYPE_ANY"
TT_TYPE_CHAR = "TYPE_CHAR"

# Comparison operators
TT_EE = "EE"
TT_NE = "NE"
TT_LT = "LT"
TT_GT = "GT"
TT_LTE = "LTE"
TT_GTE = "GTE"

# Logical operators
TT_AND = "AND"
TT_OR = "OR"
TT_NOT = "NOT"

# Symbols
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"
TT_LCURLY = "LCURLY"
TT_RCURLY = "RCURLY"
TT_LSQUARE = "LSQUARE"
TT_RSQUARE = "RSQUARE"
TT_SEMI = "SEMI"
TT_COLON = "COLON"
TT_COMMA = "COMMA"
TT_DOT = "DOT"

# Other
TT_IDENTIFIER = "IDENTIFIER"
TT_KEYWORD = "KEYWORD"
TT_EOF = "EOF"

KEYWORDS = [
    "var", "const", "if", "else", "elif", "while",
    "for", "match"," case", "default", "import", "export",
    "module", "type", "pass", "func", "return", "break",
    "continue", "true", "false", "null", "int", "float",
    "string", "boolean", "list", "char", "any", "use",
]

class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value
        self.pos_start = pos_start
        self.pos_end = pos_end
    
    def __repr__(self):
        return f"{self.type}: {self.value}" if self.value else f"{self.type}"