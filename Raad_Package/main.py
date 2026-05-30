# main.py
from lexer import Lexer
from parser import Parser
from errors import RTError
from interpreter import Interpreter
from context import Context
from symbol_table import SymbolTable

from values import Number, Boolean, Null, String, List, BuiltInFunction
import sys

# Built-in functions
def print_func(args, context):
    output = " ".join(str(arg) for arg in args)
    print(output)
    return None

def input_func(args, context):
    prompt = str(args[0]) if args else ""
    try:
        user_input = input(prompt)
        return String(user_input)
    except KeyboardInterrupt:
        return Null()

def len_func(args, context):
    if len(args) != 1:
        return None, RTError(
            None, None,
            f"len() takes expects 1 argument, got {len(args)}"
        )
    obj = args[0]
    if isinstance(obj, String):
        return Number(len(obj.value))
    elif isinstance(obj, List):
        return Number(len(obj.elements))
    else:
        return Number(0)

def type_func(args, context):
    if len(args) != 1:
        return None, RTError(
            None, None,
            f"type() expects 1 argument, got {len(args)}",
            context
        )

    obj = args[0]
    if isinstance(obj, Number):
        return String("number")
    elif isinstance(obj, String):
        return String("string")
    elif isinstance(obj, List):
        return String("list")
    elif isinstance(obj, Boolean):
        return String("boolean")
    elif isinstance(obj, Null):
        return String("null")
    return String("unknown")

def int_func(args, context):
    if len(args) != 1:
        return None, RTError(
            None, None,
            f"int() expects 1 argument, got {len(args)}",
            context
        )

    obj = args[0]
    if isinstance(obj, Number):
        return Number(int(obj.value))
    elif isinstance(obj, String):
        try:
            return Number(int(obj.value))
        except:
            return Number(0)
    return Number(0)

def str_func(args, context):
    if len(args) != 1:
        return None, RTError(
            None, None,
            f"str() expects 1 argument, got {len(args)}",
            context
        )

    return String(str(args[0]))

def range_func(args, context):
    """Handle range with 1, 2, or 3 arguments"""
    if len(args) == 1:
        # range(stop)
        start = 0
        end = int(args[0].value)
        step = 1
    elif len(args) == 2:
        # range(start, stop)
        start = int(args[0].value)
        end = int(args[1].value)
        step = 1
    elif len(args) == 3:
        # range(start, stop, step)
        start = int(args[0].value)
        end = int(args[1].value)
        step = int(args[2].value)
    else:
        return None, RTError(
            None, None,
            f"range() expects 1-3 arguments, got {len(args)}",
            context
        )

    numbers = [Number(i) for i in range(start, end, step)]
    return List(numbers)

def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    
    if error:
        return None, error
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    if ast.error:
        return None, ast.error
    
    interpreter = Interpreter()
    global_symbol_table = SymbolTable()
    
    # Built-in values
    global_symbol_table.set("true", Boolean(True))
    global_symbol_table.set("false", Boolean(False))
    global_symbol_table.set("null", Null())
    
    # Built-in functions - FIXED: range_func accepts variable args
    global_symbol_table.set("print", BuiltInFunction("print", print_func, -1))  # -1 means variable args
    global_symbol_table.set("input", BuiltInFunction("input", input_func, -1))
    global_symbol_table.set("len", BuiltInFunction("len", len_func, 1))
    global_symbol_table.set("type", BuiltInFunction("type", type_func, 1))
    global_symbol_table.set("int", BuiltInFunction("int", int_func, 1))
    global_symbol_table.set("str", BuiltInFunction("str", str_func, 1))
    global_symbol_table.set("range", BuiltInFunction("range", range_func, -1))  # -1 for variable args
    
    context = Context("<program>")
    context.symbol_table = global_symbol_table
    
    result = interpreter.visit(ast.value, context)
    
    return result.value, result.error

def shell():
    print("=" * 60)
    print("My Language v2.0 - Complete Edition")
    print("=" * 60)
    print("Features:")
    print("  • Variables (var/const)")
    print("  • Numbers, Strings, Lists")
    print("  • Arithmetic (+, -, *, /, **, //, %)")
    print("  • Assignment Operators (+=, -=, *=, /=, **=, //=, %=)")
    print("  • Increment/Decrement (++, --)")
    print("  • Comparison (==, !=, <, >, <=, >=)")
    print("  • Logical (&&, ||, !)")
    print("  • If/Elif/Else statements")
    print("  • While loops")
    print("  • Built-in functions (print, input, len, type, int, str, range)")
    print("=" * 60)
    print("Type 'exit' to quit\n")
    
    global_symbol_table = SymbolTable()
    global_symbol_table.set("true", Boolean(True))
    global_symbol_table.set("false", Boolean(False))
    global_symbol_table.set("null", Null())
    global_symbol_table.set("print", BuiltInFunction("print", print_func, -1))
    global_symbol_table.set("input", BuiltInFunction("input", input_func, -1))
    global_symbol_table.set("len", BuiltInFunction("len", len_func, 1))
    global_symbol_table.set("type", BuiltInFunction("type", type_func, 1))
    global_symbol_table.set("int", BuiltInFunction("int", int_func, 1))
    global_symbol_table.set("str", BuiltInFunction("str", str_func, 1))
    global_symbol_table.set("range", BuiltInFunction("range", range_func, -1))
    
    interpreter = Interpreter()
    line_num = 1
    
    while True:
        try:
            text = input(f"{line_num:3d} > ")
            
            if text.strip() == "exit":
                print("Goodbye!")
                break
            
            if not text.strip():
                line_num += 1
                continue
            
            lexer = Lexer("<stdin>", text)
            tokens, error = lexer.make_tokens()
            
            if error:
                print(error.as_string())
                line_num += 1
                continue
            
            parser = Parser(tokens)
            ast = parser.parse()
            
            if ast.error:
                print(ast.error.as_string())
                line_num += 1
                continue
            
            context = Context(f"line {line_num}")
            context.symbol_table = global_symbol_table
            
            result = interpreter.visit(ast.value, context)
            
            if result.error:
                print(result.error.as_string())
            elif result.value is not None:
                print(f"  → {result.value}")
            
            line_num += 1
            
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit")
        except EOFError:
            print("\nGoodbye!")
            break

def run_file(filename):
    try:
        with open(filename, 'r') as f:
            text = f.read()
        
        result, error = run(filename, text)
        
        if error:
            print(error.as_string())
        elif result is not None:
            print(result)
            
    except FileNotFoundError:
        print(f"File '{filename}' not found")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        shell()