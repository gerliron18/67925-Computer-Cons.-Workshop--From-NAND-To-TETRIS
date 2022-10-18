"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

KEYWORDS = ["class", "constructor", "function", "method", "field", "static",
            "var", "int", "char", "boolean", "void", "true", "false", "null",
            "this", "let", "do", "if", "else", "while", "return"]

SYMBOLS = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '|',
           '*', '/', '&', ',', '<', '>', '=', '~', '^', '#']


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        self.input_lines = input_stream.read().splitlines()
        self.clean_comments()
        self.index_line = 0
        self.index_inline = 0
        self.current_token = None

    def clean_comments(self):
        to_save = []
        i = 0
        while i< len(self.input_lines):
            line = self.input_lines[i]
            if '//' in line:
                comment_start_idx = line.index('//')
                to_save.append(line[:comment_start_idx].strip())
                i += 1
            elif "/*" in line:
                while "*/" not in line:
                    i += 1
                    line = self.input_lines[i]
                i += 1
            else:
                to_save.append(line.strip())
                i += 1

        self.input_lines = list(filter(None, to_save))

    def set_next_line_indices(self):
        self.index_line += 1
        self.index_inline = 0

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        return self.index_line < len(self.input_lines)

    def advance_inline_index(self):
        self.index_inline += 1

        if self.index_inline == len(self.input_lines[self.index_line]):
            self.set_next_line_indices()
            return True

        return False

    def get_cur_char(self):
        # print("index_line= " , self.index_line)
        # print("index_inline= " , self.index_inline)
        return self.input_lines[self.index_line][self.index_inline]

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        while self.get_cur_char() in [" ", "\t"]:
            self.advance_inline_index()
        if self.get_cur_char() in SYMBOLS:
            self.current_token = self.get_cur_char()
            self.advance_inline_index()
        elif self.get_cur_char() == "\"":
            self.current_token = "\""
            self.advance_inline_index()

            while self.get_cur_char() != "\"":
                self.current_token += self.get_cur_char()
                self.advance_inline_index()

            self.current_token += "\""
            self.advance_inline_index()
        else:
            self.current_token = ""
            while self.get_cur_char() != " " and \
                  self.get_cur_char() not in SYMBOLS:
                self.current_token += self.get_cur_char()
                if self.advance_inline_index():
                    break

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        if self.current_token in KEYWORDS:
            return "KEYWORD"
        elif self.current_token in SYMBOLS:
            return "SYMBOL"
        elif self.current_token.startswith('"'):
            return "STRING_CONST"
        elif self.current_token.isnumeric():
            return "INT_CONST"
        else:
            return "IDENTIFIER"

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return self.current_token.upper()

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
        """
        return self.current_token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
        """
        return self.current_token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
        """
        return int(self.current_token)

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
        """
        return self.current_token[1:-1]
