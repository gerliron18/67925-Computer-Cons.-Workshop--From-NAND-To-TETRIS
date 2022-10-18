"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
from JackTokenizer import JackTokenizer

TOKEN_TYPES_DICT = {"KEYWORD": "keyword", "SYMBOL": "symbol",
              "STRING_CONST": "stringConstant", "INT_CONST": "integerConstant",
              "IDENTIFIER": "identifier"}

OP_LIST = ["+", "-", "*", "/", "|", "&", "<", ">", "=", "^", "#", "~"]

UNARY_OP_LIST = ["-", "~", "#", "^"]

CONVERT_OP = {"&": "&amp;", "<": "&lt;" , ">": "&gt;"}


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: JackTokenizer, output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.tokenizer = input_stream
        self.output_stream = output_stream

    def _write_token(self) -> None:
        current_token = self.tokenizer.current_token
        token_type = self.tokenizer.token_type()
        if token_type == "KEYWORD":
            current_token = self.tokenizer.keyword().lower()
        elif token_type == "SYMBOL":
            current_token = self.tokenizer.symbol()
        elif token_type == "STRING_CONST":
            current_token = self.tokenizer.string_val()
        elif token_type == "INT_CONST":
            current_token = self.tokenizer.int_val()
        elif token_type == "IDENTIFIER":
            current_token = self.tokenizer.identifier()

        if current_token in CONVERT_OP.keys(): # Handle OP conversion
            current_token = CONVERT_OP[current_token]

        print("current_token: ", self.tokenizer.current_token)
        tag = TOKEN_TYPES_DICT[token_type]
        self.output_stream.write(f"<{tag}> {current_token} </{tag}>\n")
        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.output_stream.write("<class>\n")
        self.tokenizer.advance()
        self._write_token() # writes "class"
        self._write_token() # writes class name
        self._write_token() # writes "{"

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
            else:
                print("ERROR from compile_class: " + current_token)
                raise Exception

        self._write_token() # writes "}"
        self.output_stream.write("</class>\n")

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        self.output_stream.write("<classVarDec>\n")
        while self.tokenizer.current_token != ";" and self.tokenizer.has_more_tokens():
            print("current_token is: ", self.tokenizer.current_token)
            self._write_token()

        self._write_token() # writes ";"
        self.output_stream.write("</classVarDec>\n")

    def _compile_subroutine_body(self):
        self.output_stream.write("<subroutineBody>\n")
        self._write_token()  # writes "{"
        while self.tokenizer.current_token == "var":
            self.compile_var_dec()
        self.compile_statements()
        self._write_token()  # writes "}"
        self.output_stream.write("</subroutineBody>\n")

    def compile_subroutine(self) -> None:
        """Compiles a complete method, function, or constructor."""
        self.output_stream.write("<subroutineDec>\n")
        self._write_token() # writes "function/method/constructor"

        while self.tokenizer.current_token != "(" and self.tokenizer.has_more_tokens():
            self._write_token()

        self._write_token() # writes "("
        self.compile_parameter_list()
        self._write_token() # writes ")"

        self._compile_subroutine_body()

        self.output_stream.write("</subroutineDec>\n")

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        self.output_stream.write("<parameterList>\n")

        while self.tokenizer.current_token != ")" and self.tokenizer.has_more_tokens():
            self._write_token()

        self.output_stream.write("</parameterList>\n")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.output_stream.write("<varDec>\n")
        self._write_token() # writes "var"
        self._write_token() # writes variable type

        while self.tokenizer.current_token != ";" and self.tokenizer.has_more_tokens():
            self._write_token()

        self._write_token() # writes ";"

        self.output_stream.write("</varDec>\n")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        self.output_stream.write("<statements>\n")

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
            else:
                print("ERROR from compile_statement: " + self.tokenizer.current_token)
                raise Exception

        self.output_stream.write("</statements>\n")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.output_stream.write("<doStatement>\n")
        self._write_token() # writes "do"
        while self.tokenizer.current_token != "(" and self.tokenizer.has_more_tokens():
            self._write_token()

        self._write_token() # writes "("
        self.compile_expression_list()
        self._write_token() # writes ")"

        self._write_token() # writes ";"
        self.output_stream.write("</doStatement>\n")

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.output_stream.write("<letStatement>\n")
        self._write_token()  # writes "let"
        self._write_token() # writes an identifier

        if self.tokenizer.current_token != "=":
            self._write_token()  # [
            self.compile_expression()
            self._write_token()  # ]

        self._write_token() # writes "="

        self.compile_expression()

        self._write_token() # writes ";"

        self.output_stream.write("</letStatement>\n")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.output_stream.write("<whileStatement>\n")
        self._write_token() # writes "while"
        self._write_token() # writes "("

        self.compile_expression()

        self._write_token()  # writes ")"
        self._write_token()  # writes "{"

        self.compile_statements()

        self._write_token()  # writes "}"
        self.output_stream.write("</whileStatement>\n")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.output_stream.write("<returnStatement>\n")
        self._write_token() # writes "return"

        if self.tokenizer.current_token != ";":
            self.compile_expression()

        self._write_token() # writes ";"
        self.output_stream.write("</returnStatement>\n")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.output_stream.write("<ifStatement>\n")
        self._write_token() # writes "if"
        self._write_token() # writes "("

        self.compile_expression()

        self._write_token() # writes ")"
        self._write_token() # writes "{"

        self.compile_statements()

        self._write_token() # writes "}"

        if self.tokenizer.current_token == "else":
            self.compile_else()

        self.output_stream.write("</ifStatement>\n")

    def compile_else(self):
        self._write_token()  # writes "else"
        self._write_token()  # writes "{"

        self.compile_statements()

        self._write_token() # writes "}"

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.output_stream.write("<expression>\n")

        self.compile_term()

        while self.tokenizer.current_token in OP_LIST and self.tokenizer.has_more_tokens():
            self._write_token() # writes the op
            self.compile_term()

        self.output_stream.write("</expression>\n")

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        self.output_stream.write("<term>\n")

        def compile_term_helper():
            if self.tokenizer.current_token == "(":
                self._write_token()  # writes "("
                self.compile_expression()
                self._write_token()  # writes ")"
                return

            if self.tokenizer.current_token in UNARY_OP_LIST:
                self._write_token()  # writes unary op
                self.compile_term()
                return

            self._write_token()
            if self.tokenizer.current_token == "[":
                self._write_token() # writes "["
                self.compile_expression()
                self._write_token() # writes "]"
            elif self.tokenizer.current_token == "(":
                self._write_token() # writes "("
                self.compile_expression_list()
                self._write_token() # writes ")"
            elif self.tokenizer.current_token == ".":
                self._write_token() # writes "."
                compile_term_helper()

        compile_term_helper()
        self.output_stream.write("</term>\n")

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.output_stream.write("<expressionList>\n")
        print("Expression_list called")
        while self.tokenizer.current_token != ")" and self.tokenizer.current_token != ";" and self.tokenizer.has_more_tokens():
            self.compile_expression()
            if self.tokenizer.current_token == ",":
                self._write_token() # suppose to be ","

        self.output_stream.write("</expressionList>\n")



