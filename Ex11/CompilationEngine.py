"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
from JackTokenizer import JackTokenizer
from VMWriter import VMWriter
from SymbolTable import SymbolTable, VAR, FIELD, STATIC, ARG, CONST, LOCAL, \
    THIS, THAT, POINTER, TEMP
import re

TOKEN_TYPES_DICT = {"KEYWORD": "keyword", "SYMBOL": "symbol",
              "STRING_CONST": "stringConstant", "INT_CONST": "integerConstant",
              "IDENTIFIER": "identifier"}

OP_DICT = {"#": 'SHIFTLEFT', "^": 'SHIFTRIGHT', "+": "ADD", "-": "SUB", "&": "AND", "|": "OR", "<": "LT", ">": "GT","=":"EQ", "~":"NOT"}
OP_LIST = ['#', '^', '+', '-', '&', '|', '<', '>', '=', '~', '*', '/']


UNARY_OP_LIST = ["-", "~", "#", "^"]

CONVERT_OP = {"&": "&amp;", "<": "&lt;" , ">": "&gt;"}


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, tokenizer: JackTokenizer, vmwriter: VMWriter) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param tokenizer: The JackTokenizer to read from.
        :param output_stream: VMWriter to use to write commands.
        """
        self.vmwriter = vmwriter
        self.tokenizer = tokenizer
        self.symbol_table = SymbolTable()
        self.class_name = None
        self.label_counter = 0

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.tokenizer.advance()
        # current token = "class"
        self.tokenizer.advance()
        # current token = class name
        self.class_name = self.tokenizer.current_token
        self.tokenizer.advance()
        # current token = {
        self.tokenizer.advance()

        while self.tokenizer.has_more_tokens():
            current_token = self.tokenizer.current_token
            if current_token in ["function", "constructor", "method"]:
                self.compile_subroutine()
            elif current_token == "field" or current_token == "static":
                self.compile_class_var_dec()
            elif current_token == "do":
                self.compile_do()
            elif current_token == "let":
                self.compile_let()
            elif current_token == "return":
                self.compile_return()
            elif current_token == "var":
                self.compile_var_dec()
            elif current_token == "while":
                self.compile_while()
            elif current_token == "if":
                self.compile_if()

        # current token is "}" and no more tokens in this class

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        self.compile_var_static_field_dec()

    def compile_local_vars(self):
        vars_num = 0
        while self.tokenizer.current_token == "var":
            vars_num += self.compile_var_dec()
        return vars_num

    def compile_subroutine(self) -> None:
        """Compiles a complete method, function, or constructor."""
        self.symbol_table.start_subroutine()

        subroutine_type = self.tokenizer.current_token  # function, method, constructor
        self.tokenizer.advance()
        if subroutine_type == "method":
            self.symbol_table.define("this", self.class_name, "ARG")

        return_type = self.tokenizer.current_token  # void or other
        self.tokenizer.advance()
        subroutine_name = self.tokenizer.current_token
        self.tokenizer.advance()

        self.tokenizer.advance()  # current token: "("
        params_num = self.compile_parameter_list()
        self.tokenizer.advance()  # current token: ")"
        self.tokenizer.advance()  # current token: "{"

        local_vars_num = self.compile_local_vars()
        self.vmwriter.write_function(f"{self.class_name}.{subroutine_name}", local_vars_num)

        if subroutine_type == "constructor":
            fields_num = self.symbol_table.var_count("FIELD")
            self.vmwriter.write_push("CONST", fields_num)
            self.vmwriter.write_call("Memory.alloc", 1)
            self.vmwriter.write_pop("POINTER", 0)

        if subroutine_type == "method":
            self.vmwriter.write_push("ARG", 0)
            self.vmwriter.write_pop("POINTER", 0)

        self.compile_statements()
        self.tokenizer.advance()  # "}"

    def compile_parameter_list(self) -> int:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        # function a(int b, int c)
        params_num = 0
        while self.tokenizer.current_token != ")" and self.tokenizer.has_more_tokens():
            param_type = self.tokenizer.current_token
            self.tokenizer.advance()
            param_name = self.tokenizer.current_token
            self.tokenizer.advance()

            self.symbol_table.define(param_name, param_type, ARG)
            params_num += 1
            if self.tokenizer.current_token == ",":
                self.tokenizer.advance()
        return params_num

    def compile_var_dec(self) -> None:
        return self.compile_var_static_field_dec()

    def compile_var_static_field_dec(self) -> None:
        """Compiles a var declaration. Assumes that the current
        token is var, field or static."""
        # var int a, b, c;
        vars_num = 0
        kind = self.tokenizer.current_token # var, static, field
        self.tokenizer.advance()  # kind
        var_type = self.tokenizer.current_token
        self.tokenizer.advance() #  var type

        while self.tokenizer.current_token != ";" and self.tokenizer.has_more_tokens():
            var_name = self.tokenizer.current_token
            self.tokenizer.advance()
            if var_name != ',':
                self.symbol_table.define(var_name, var_type, kind.upper())
                vars_num += 1

        self.tokenizer.advance()  # ";"
        return vars_num

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        while self.tokenizer.current_token != "}" and self.tokenizer.has_more_tokens():
            if self.tokenizer.current_token == "let":
                self.compile_let()
            elif self.tokenizer.current_token == "do":
                self.compile_do()
            elif self.tokenizer.current_token == "if":
                self.compile_if()
            elif self.tokenizer.current_token == "while":
                self.compile_while()
            elif self.tokenizer.current_token == "return":
                self.compile_return()

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.tokenizer.advance() # first token is "do" # do Class.funcName(fdfdfd);
        callab = '' # callable object, may be a function or obj.func
        while self.tokenizer.current_token != "(" and self.tokenizer.has_more_tokens():
            callab += self.tokenizer.current_token
            self.tokenizer.advance()
        self.tokenizer.advance()  # token is "("
        arguments = self.get_expression_list()
        self.compile_func_call(callab, arguments)
        self.tokenizer.advance()  # token is ";"

        self.vmwriter.write_pop("TEMP", 0)

    def compile_let(self) -> None:
        """Compiles a let statement."""
        # let <var-name> = expression;
        def array_compile_let():
            self.vmwriter.write_push(segment, idx)
            self.compile_expression(indexing_exp)
            self.vmwriter.write_arithmetic("ADD")
            self.compile_expression(exp)
            self.vmwriter.write_pop("TEMP", 0)
            self.vmwriter.write_pop("POINTER", 1)
            self.vmwriter.write_push("TEMP", 0)
            self.vmwriter.write_pop("THAT", 0)
            self.tokenizer.advance() # ;

        def reg_compile_let():
            self.compile_expression(exp)
            self.tokenizer.advance() # ;
            self.vmwriter.write_pop(segment, idx)

        self.tokenizer.advance() # let
        var_name = self.tokenizer.current_token
        segment = self.symbol_table.segment_of(var_name)
        idx = self.symbol_table.index_of(var_name)
        array_let = False
        self.tokenizer.advance()
        if self.tokenizer.current_token == "[":
            array_let = True
            self.tokenizer.advance() # "["
            indexing_exp = self.get_expression_until_closing_parenthases("[")

        self.tokenizer.advance() # =

        exp = ""
        while self.tokenizer.current_token != ";":
            exp += self.tokenizer.current_token
            self.tokenizer.advance()

        if array_let:
            array_compile_let()
        else:
            reg_compile_let()


    def get_expression_until_closing_parenthases(self, paren_type):
        """

        :param paren_type: "(" or "["
        :return:
        """
        if paren_type == "(":
            open_paren = "("
            close_paren = ")"
        else: # paren_type = "["
            open_paren = "["
            close_paren = "]"

        exp = ""
        parenthases_counter = 1  # we already saw first open
        while parenthases_counter > 0:
            exp += self.tokenizer.current_token
            if self.tokenizer.current_token == open_paren:
                parenthases_counter += 1
            if self.tokenizer.current_token == close_paren:
                parenthases_counter -= 1
            self.tokenizer.advance()

        return exp[:-1]

    def compile_while(self) -> None:
        """Compiles a while statement."""
        # while (exp){ statements }
        L1_label = f"L1_{self.label_counter}"
        L2_label = f"L2_{self.label_counter}"
        self.label_counter += 1
        self.vmwriter.write_label(L1_label)
        self.tokenizer.advance() # while
        self.tokenizer.advance() # (

        exp = self.get_expression_until_closing_parenthases("(")
        self.compile_expression(exp)

        self.tokenizer.advance() # {
        self.vmwriter.write_arithmetic("NOT")
        self.vmwriter.write_if(L2_label)
        self.compile_statements()
        self.tokenizer.advance() # }
        self.vmwriter.write_goto(L1_label)
        self.vmwriter.write_label(L2_label)

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.tokenizer.advance()  # "return"

        if self.tokenizer.current_token == ';': # return;
            self.vmwriter.write_push(CONST, 0)

        else:
            # e.g., return a+b;
            exp = ""
            while self.tokenizer.current_token != ";":
                exp += self.tokenizer.current_token
                self.tokenizer.advance()

            if exp == "this":  # in constructors the return statement is always "return this;"
                self.vmwriter.write_push("POINTER", 0)
            else:
                self.compile_expression(exp)

        self.tokenizer.advance()  # ";"
        self.vmwriter.write_return()


    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # if (exp) { (...statements1...); } else { statements2 }
        self.tokenizer.advance()# if
        self.tokenizer.advance()  # (
        exp = self.get_expression_until_closing_parenthases("(")
        self.compile_expression(exp)
        self.tokenizer.advance() # {

        self.vmwriter.write_arithmetic("NOT")
        L1_label = f"L1_{self.label_counter}"
        L2_label = f"L2_{self.label_counter}"
        self.label_counter += 1
        self.vmwriter.write_if(L1_label)
        self.compile_statements() # statements1
        self.tokenizer.advance() # }
        self.vmwriter.write_goto(L2_label)

        self.vmwriter.write_label(L1_label)

        if self.tokenizer.current_token == "else":
            self.tokenizer.advance() # else
            self.tokenizer.advance() # {
            self.compile_statements() # statements2
            self.tokenizer.advance() # }

        self.vmwriter.write_label(L2_label)

    def output_operator(self, op):
        if op == "*":
            self.vmwriter.write_call("Math.multiply", 2)
        elif op == "/":
            self.vmwriter.write_call("Math.divide", 2)
        else:
            self.vmwriter.write_arithmetic(OP_DICT[op])

    def get_params_from_param_str(self, param_as_str: str) -> list:
        params = self.split_exp_by_comma(param_as_str)
        params = list(map(str.strip, params))
        if "" in params:
            params.remove("")
        return params

    def split_exp_by_comma(self, expression: str) -> list:
        res = []
        i = 0
        start_idx = 0
        while i < len(expression):
            if expression[i] == "(":
                inner_exp, rest_of_exp, split_idx = self.split_expression_by_closing_parenthases(expression[i+1:], "(")
                i = split_idx + i + 1  # skip the whole part of f(...)
            elif expression[i] == "[":
                inner_exp, rest_of_exp, split_idx = self.split_expression_by_closing_parenthases(expression[i+1:], "[")
                i = split_idx + i + 1  # skip the whole part of arr[...]
            elif expression[i] == "\"":
                i += 1
                while expression[i] != "\"":
                    i += 1
                i+=1
            else:
                if expression[i] == ",":
                    res.append(expression[start_idx:i])
                    start_idx = i+1
                i += 1

        res.append(expression[start_idx:i])  # last argument

        return res

    def split_expression_by_closing_parenthases(self, expression, paren_type):
        """
        :param expression:
        :param paren_type:  "(" or "["
        :return:
        """
        if paren_type == "(":
            open_paren = "("
            close_paren = ")"
        else:  # paren_type = "["
            open_paren = "["
            close_paren = "]"

        inner_exp_res = ""
        parenthases_counter = 1  # we already saw first open
        char_idx = 0
        while parenthases_counter > 0:
            inner_exp_res += expression[char_idx]
            if expression[char_idx] == open_paren:
                parenthases_counter += 1
            if expression[char_idx] == close_paren:
                parenthases_counter -= 1
            char_idx += 1

        return inner_exp_res[:-1], expression[char_idx:], char_idx

    def compile_expression(self, exp: str) -> None:
        """Compiles an expression."""

        def clean_exp(expression: str):
            expression = expression.strip()
            if "\"" in expression:
                first_quote_idx = expression.index("\"")
                before_quote = expression[:first_quote_idx].replace(' ', '')
                second_quote_idx = expression[first_quote_idx+1:].index("\"") + first_quote_idx+1
                after_quote = expression[second_quote_idx+1:].replace(' ', '')
                quote = expression[first_quote_idx:second_quote_idx+1]

                expression = before_quote + quote + after_quote

            return expression

        def split_exp_by_parenthases(expression):
            first_part = ""
            second_part = ""
            parenthases_counter = 1
            for i in range(1, len(expression)):
                char = expression[i]
                if char == "(":
                    parenthases_counter += 1
                if char == ")":
                    parenthases_counter -= 1

                if parenthases_counter == 0:
                    second_part = expression[i+1:]
                    break
                else:
                    first_part += char

            return first_part, second_part

        def find_max_valid_operator_index(expression): # a < -1
            def is_operator_valid(j):
                cur_char = expression[j]
                if cur_char not in OP_LIST:
                    return False
                left_substring = expression[:j]
                return left_substring.count('(') == left_substring.count(')') \
                    and left_substring.count('[') == left_substring.count(']')

            for i in range(len(expression)-1, -1, -1):
                if is_operator_valid(i):
                    if i-1 >= 0 and is_operator_valid(i-1):
                        return i-1
                    else:
                        return i

        exp = clean_exp(exp)

        if str(exp).isdigit(): # exp is a constant
            self.vmwriter.write_push(CONST, int(exp))
            return

        if exp == "true":
            self.vmwriter.write_push(CONST, 1)
            self.vmwriter.write_arithmetic("NEG")
            return

        if exp == "false" or exp == "null":
            self.vmwriter.write_push(CONST, 0)
            return

        if self.symbol_table.includes(exp):
            segment_of = self.symbol_table.segment_of(exp)
            var_idx = self.symbol_table.index_of(exp)
            self.vmwriter.write_push(segment_of, var_idx)
            return

        if exp.startswith("\""):
            string_len = len(exp)-2  # length without ""
            self.vmwriter.write_push("CONST", string_len)
            self.vmwriter.write_call("String.new", 1)
            for c in exp[1:-1]:
                self.vmwriter.write_push("CONST", ord(c))
                self.vmwriter.write_call("String.appendChar", 2)
            return

        if exp.startswith("("):
            unparenthasized_exp, rest_of_exp = split_exp_by_parenthases(exp)
            self.compile_expression(unparenthasized_exp)
            if len(rest_of_exp) > 0: # (unparenthasized_exp) op another_exp
                self.compile_expression(rest_of_exp[1:])
                self.output_operator(rest_of_exp[0])
            return

        if exp[0] in OP_DICT.keys():  # <op> <expression>
            self.compile_expression("".join(exp[1:]))
            if exp[0] == "-":
                self.vmwriter.write_arithmetic("NEG")
            else:
                self.output_operator(exp[0])
            return

        match_func_call = re.fullmatch(r"[^*#^+\-&|<>=~]+\(.*\)", exp)
        if bool(match_func_call): # exp is f(exp1, exp2, ...)
            inner_expressions_as_str, rest_of_exp, idx = self.split_expression_by_closing_parenthases(exp[exp.index("(")+1:], "(")
            inner_expressions = self.get_params_from_param_str(inner_expressions_as_str)
            callab = exp[:exp.index("(")]  # either func_name or obj.func_name
            self.compile_func_call(callab, inner_expressions)

            if len(rest_of_exp) > 0:  # func(exp1,exp2) op expression
                self.compile_expression(rest_of_exp[1:])
                self.output_operator(rest_of_exp[0])

            return

        match_array = re.fullmatch(r"[^#^+\-&|<>=~]+\[.+]", exp)
        if bool(match_array): # a[i+j]
            array_name = exp[:exp.index("[")]
            array_segment = self.symbol_table.segment_of(array_name)
            array_idx = self.symbol_table.index_of(array_name)
            self.vmwriter.write_push(array_segment, array_idx)
            inner_expression, rest_of_exp, idx = self.split_expression_by_closing_parenthases(exp[exp.index("[")+1:], "[")
            self.compile_expression(inner_expression)

            self.vmwriter.write_arithmetic("ADD")
            self.vmwriter.write_pop("POINTER", 1)
            self.vmwriter.write_push("THAT", 0)
            if len(rest_of_exp) > 0: # arr[inner_exp] op expression
                self.compile_expression(rest_of_exp[1:])
                self.output_operator(rest_of_exp[0])
            return

        else:
            idx = find_max_valid_operator_index(exp)
            self.compile_expression(exp[:idx])
            self.compile_expression(exp[idx + 1:])
            self.output_operator(exp[idx])
            return

    def compile_func_call(self, func_call: str, arguments: list):
        callab_parts = func_call.split(".")
        if len(callab_parts) > 1 and self.symbol_table.includes(callab_parts[0]):  # obj.func_name
            [objname, func_name] = func_call.split(".")
            obj_segment = self.symbol_table.segment_of(objname)
            obj_idx = self.symbol_table.index_of(objname)
            obj_class = self.symbol_table.type_of(objname)
            self.vmwriter.write_push(obj_segment, obj_idx)
            self.compile_expression_list(arguments)
            self.vmwriter.write_call(f"{obj_class}.{func_name}", len(arguments) + 1)
        elif len(callab_parts) > 1 and not self.symbol_table.includes(callab_parts[0]): # Class.func_name
            func_name = func_call
            self.compile_expression_list(arguments)
            self.vmwriter.write_call(func_name, len(arguments))
        else: # just func_name, meaning this is this class's method (e.g. "draw" in "Square" class)
            func_name = func_call
            self.vmwriter.write_push("POINTER", 0)
            self.compile_expression_list(arguments)
            self.vmwriter.write_call(f"{self.class_name}.{func_name}", len(arguments)+1)

    def get_expression_list(self) -> list:
        # f(a+e,b,c)
        # f(a)
        exp_list_as_str = ""
        while self.tokenizer.current_token != ";":
            exp_list_as_str += self.tokenizer.current_token
            self.tokenizer.advance() # will also advance over the closing ")" of the expression list

        exp_list_as_str = exp_list_as_str[:-1]
        exp_list = self.get_params_from_param_str(exp_list_as_str)
        return exp_list

    def compile_expression_list(self, exp_list) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        for exp in exp_list:
            self.compile_expression(exp)
