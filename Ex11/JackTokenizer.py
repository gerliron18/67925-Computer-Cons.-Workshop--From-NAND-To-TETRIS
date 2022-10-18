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
        self.input_raw = input_stream.read()
        self.input_raw = self.clean_long_comments()
        self.input_raw = self.clean_short_comments_alt()
        self.input_lines = list(map(str.strip, self.input_raw.splitlines()))
        self.input_lines = list(filter(lambda line: len(line) > 0, self.input_lines))
        self.index_line = 0
        self.index_inline = 0
        self.current_token = None

    def clean_comments(self, long_or_short: str):
        # if long_or_short == 'short':
        comment_open = '//'
        comment_close = '\n'
        if long_or_short == 'long':
            comment_open = '/*'
            comment_close = '*/'

        cleaned_raw_input = ''
        i=0
        in_string_const = False
        in_comment = False
        while i < len(self.input_raw)-1:
            cur_char = self.input_raw[i]
            next_char = self.input_raw[i+1]
            if cur_char == '\"' and not in_comment:
                if in_string_const:
                    in_string_const = False
                else:
                    in_string_const = True

            # closing comment
            if long_or_short == 'long':
                if cur_char+next_char == comment_close and not in_string_const:
                    i += 2
                    in_comment = False
                    continue
            if long_or_short == 'short':
                if cur_char == comment_close and not in_string_const:
                    cleaned_raw_input += cur_char
                    i += 1
                    in_comment = False
                    continue
            ####

            if cur_char+next_char == comment_open and not in_string_const:
                i += 2
                in_comment = True
                continue

            if not in_comment or in_string_const:
                cleaned_raw_input += cur_char

            i += 1

        if not in_comment:
            cleaned_raw_input += self.input_raw[-1]

        return cleaned_raw_input

    def clean_short_comments_alt(self):
        return self.clean_comments("short")

    def clean_long_comments(self):
        return self.clean_comments("long")

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
        return self.input_lines[self.index_line][self.index_inline]

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        while self.get_cur_char().isspace():
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
            while not self.get_cur_char().isspace() and \
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
