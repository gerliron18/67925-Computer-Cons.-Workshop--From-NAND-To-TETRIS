"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

C_ARITHMETIC = "C_ARITHMETIC"
C_PUSH = "C_PUSH"
C_POP = "C_POP"
C_LABEL = "C_LABEL"
C_CALL = "C_CALL"
C_GOTO = "C_GOTO"
C_FUNCTION = "C_FUNcTION"
C_RETURN = "C_RETURN"
C_IF = "C_IF"


class Parser:
    """
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.
    """

    cmd_dict = {"add": C_ARITHMETIC, "sub": C_ARITHMETIC, "neg": C_ARITHMETIC,
                "eq": C_ARITHMETIC, "gt": C_ARITHMETIC, "lt": C_ARITHMETIC,
                "and": C_ARITHMETIC, "or": C_ARITHMETIC, "not": C_ARITHMETIC,
                "shiftleft": C_ARITHMETIC, "shiftright": C_ARITHMETIC,
                "push": C_PUSH, "pop": C_POP, "goto": C_GOTO, "if-goto": C_IF,
                "label": C_LABEL, "call": C_CALL, "function": C_FUNCTION,
                "return": C_RETURN
                }
    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        # A good place to start is:
        self.input_lines = input_file.read().splitlines()
        self.cur_line = None
        self.cur_index = -1
        self.file_len = len(self.input_lines)
        self.cur_line_parts = None

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return not self.cur_index == self.file_len - 1


    def advance(self) -> None:
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        if (self.has_more_commands()):
            self.cur_index += 1
            self.cur_line = self.input_lines[self.cur_index]
            if self.cur_line.startswith("//") or self.cur_line == "":
                self.advance()
            self.cur_line_parts = self.cur_line.split()

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        return Parser.cmd_dict[self.cur_line_parts[0]]

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        if (self.command_type() == C_ARITHMETIC):
            return self.cur_line_parts[0]
        elif (len(self.cur_line_parts) >= 2):
            return self.cur_line_parts[1]
        else:
            return ""

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        if (len(self.cur_line_parts) >= 3):
            return int(self.cur_line_parts[2])
        else:
            return -1
