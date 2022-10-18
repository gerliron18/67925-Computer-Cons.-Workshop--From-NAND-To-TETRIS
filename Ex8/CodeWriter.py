"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

import Parser

COMPARISON_TEXT = "D=M-D\n@WRITET{count}\nD;{true_jmp}\n@WRITEF{count}\nD;{false_jmp}\n"
BINARY_OPERATIONS = {"add": "M=D+M\n", "sub": "M=M-D\n", "and": "M=D&M\n",
                     "or": "M=D|M\n", "gt": None, "lt": None, "eq": None}
COMPARISON_JUMP_DICT = {"gt": {"true_jmp": "JGT", "false_jmp": "JLE"},
                        "lt": {"true_jmp": "JLT", "false_jmp": "JGE"},
                        "eq": {"true_jmp": "JEQ", "false_jmp": "JNE"}}
BINARY_OPERATION_PREFIX = "@SP\nM=M-1\nA=M\nD=M\n@SP\nM=M-1\nA=M\n"
INCREASE_SP = "@SP\nM=M+1\n"
COMPARISON_SUFFIX = "(WRITET{count})\n@SP\nA=M\nM=-1\n@END{count}\n0;JMP\n(WRITEF{count})\n@SP\nA=M\nM=0\n(END{count})\n"
COMPARISON_CMD = ["lt", "gt", "eq"]

# -----------------
UNARY_OPERATION_PREFIX = "@SP\nM=M-1\nA=M\n"
UNARY_OPERATIONS = {"neg": "M=-M\n",
                    "not": "M=!M\n",
                    "shiftleft": "M=M<<\n",
                    "shiftright": "M=M>>\n"}

# -----------------
SEGMENTS_NAMES_DICT = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}

# -----------------push
constant_push = "//push constant {i}\n@{i}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"

reg_segment_push = "//push {segment_name} {i}\n@{i}\nD=A\n@{segment_address}\nA={segment_address_getter}+D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"

pointer_push = "//push pointer {i}\n@{i}\nD=A\n@THIS\nA=D+A\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"

static_push = "//push static {i}\n@{file_name}.{i}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"

# -----------------pop
pop_segment = "//pop {segment_name} {i}\n@{i}\nD=A\n@{segment_address}\nD=D+{segment_address_getter}\n@address\nM=D\n@SP\nM=M-1\nA=M\nD=M\n@address\nA=M\nM=D\n"

pop_pointer = "//pop pointer {i}\n@{i}\nD=A\n@THIS\nD=D+A\n@address\nM=D\n@SP\nM=M-1\nA=M\nD=M\n@address\nA=M\nM=D\n"

pop_static = "//pop static {i}\n@SP\nM=M-1\nA=M\nD=M\n@{file_name}.{i}\nM=D\n"


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.output_stream = output_stream
        self.comparison_cmd_counter = 0
        self.file_name = None
        self.counter = 0
        self.func_name = None

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        self.file_name = filename
        self.output_stream.write("// " + filename + "\n")

    def write_arithmetic(self, command: str) -> None:
        """Writes the assembly code that is the translation of the given 
        arithmetic command.

        Args:
            command (str): an arithmetic command.
        """
        cmd_translation = ""
        if command in BINARY_OPERATIONS.keys():
            if (command in COMPARISON_CMD):
                self.comparison_cmd_counter += 1
                cmd_translation = BINARY_OPERATION_PREFIX + \
                                  COMPARISON_TEXT.format(
                                      true_jmp = COMPARISON_JUMP_DICT[command]["true_jmp"],
                                      false_jmp = COMPARISON_JUMP_DICT[command]["false_jmp"],
                                      count=self.comparison_cmd_counter) + \
                                  COMPARISON_SUFFIX.format(
                                      count=self.comparison_cmd_counter) + \
                                  INCREASE_SP
            else:
                cmd_translation = BINARY_OPERATION_PREFIX + \
                              BINARY_OPERATIONS[command] + INCREASE_SP

        elif command in UNARY_OPERATIONS.keys():
            cmd_translation = UNARY_OPERATION_PREFIX + \
                              UNARY_OPERATIONS[command] + INCREASE_SP

        if command == "gt" or command == "lt" or command == "eq":
            self.has_comparison_cmd = True

        self.output_stream.write("//" + command + "\n" + cmd_translation)

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes the assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        if command == Parser.C_PUSH:
            if segment == "constant":
                self.output_stream.write(constant_push.format(i=index))
            elif segment == "temp":
                self.output_stream.write(
                    reg_segment_push.format(
                        segment_name=segment, i=index,
                        segment_address=5, segment_address_getter="A"))
            elif segment == "pointer":
                self.output_stream.write(pointer_push.format(i=index))
            elif segment == "static":
                self.output_stream.write(static_push.format(
                    file_name=self.file_name, i=index))
            else:
                self.output_stream.write(
                    reg_segment_push.format(
                        segment_name=segment, i=index,
                        segment_address=SEGMENTS_NAMES_DICT[segment],
                        segment_address_getter="M"))
        elif command == Parser.C_POP:
            if segment == "constant":
                return
            if segment == "temp":
                self.output_stream.write(
                    pop_segment.format(
                        segment_name=segment, i=index, segment_address=5,
                        segment_address_getter="A"
                    )
                )
            elif segment == "pointer":
                self.output_stream.write(pop_pointer.format(i=index))
            elif segment == "static":
                self.output_stream.write(pop_static.format(
                    file_name=self.file_name, i=index))
            else:
                self.output_stream.write(
                    pop_segment.format(
                        segment_address=SEGMENTS_NAMES_DICT[segment], i=index,
                        segment_name=segment, segment_address_getter="M"
                    )
                )

    def write_label(self, label):
        self.output_stream.write("// label {label}\n({label})\n".format(label=label))

    def write_goto(self, label):
        self.output_stream.write("// goto {label}\n@{label}\n0;JMP\n".format(label=label))

    def write_if(self, label):
        self.output_stream.write("// if-goto {label}\n@SP\nM=M-1\nA=M\nD=M\n@{label}\nD;JNE\n".format(label=label))
    def write_function(self, function_name, num_vars):
        self.func_name = function_name
        self.output_stream.write("// function {function_name} {num_vars}\n".format(
            function_name=function_name, num_vars=num_vars))
        self.write_label(function_name)
        for i in range(num_vars):
            self.output_stream.write("@SP\nA=M\nM=0\n@SP\nM=M+1\n")

    def write_call(self, function_name, num_vars):
        self.func_name = function_name
        self.output_stream.write("// call {function_name} {num_vars}\n".format(
            function_name=function_name, num_vars=num_vars))

        self.output_stream.write("// push returnAddress\n@{function_name}.ret.{counter}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n".format(function_name=function_name, counter=self.counter, filename=self.file_name))
        self.output_stream.write("// push LCL\n@LCL\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        self.output_stream.write("// push ARG\n@ARG\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        self.output_stream.write("// push THIS\n@THIS\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        self.output_stream.write("// push THAT\n@THAT\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        self.output_stream.write("// ARG=SP-5-num_vars\n@SP\nD=M\n@5\nD=D-A\n@{num_vars}\nD=D-A\n@ARG\nM=D\n" \
                                 .format(num_vars=num_vars))

        self.output_stream.write("// LCL=SP\n@SP\nD=M\n@LCL\nM=D\n")
        self.write_goto(function_name)
        self.write_label("{func_name}.ret.{counter}".format(func_name=function_name, counter=self.counter))

        self.counter += 1

    def write_return(self):
        self.output_stream.write("// return\n")
        self.output_stream.write("// endFrame=LCL\n@LCL\nD=M\n@endFrame\nM=D\n")
        self.output_stream.write("// retAddr = *(endFrame-5)\n@endFrame\nD=M\n@5\nA=D-A\nD=M\n@retAddr\nM=D\n")
        self.output_stream.write("// *ARG=pop()\n@SP\nM=M-1\nA=M\nD=M\n@ARG\nA=M\nM=D\n")
        self.output_stream.write("// SP=ARG+1\n@ARG\nD=M\n@SP\nM=D+1\n")
        self.output_stream.write("// THAT=*(endFrame-1)\n@endFrame\nA=M-1\nD=M\n@THAT\nM=D\n")
        self.output_stream.write("// THIS=*(endFrame-2)\n@endFrame\nD=M\n@2\nA=D-A\nD=M\n@THIS\nM=D\n")
        self.output_stream.write("// ARG=*(endFrame-3)\n@endFrame\nD=M\n@3\nA=D-A\nD=M\n@ARG\nM=D\n")
        self.output_stream.write("// LCL=*(endFrame-4)\n@endFrame\nD=M\n@4\nA=D-A\nD=M\n@LCL\nM=D\n")
        self.output_stream.write("// goto retAddr\n@retAddr\nA=M\n0;JMP\n")

    def write_init(self):
        self.output_stream.write("// boostrap\n// SP=256\n@256\nD=A\n@SP\nM=D\n")
        self.write_call("Sys.init", 0)

    def close(self) -> None:
        """Closes the output file."""
        self.output_stream.close()
