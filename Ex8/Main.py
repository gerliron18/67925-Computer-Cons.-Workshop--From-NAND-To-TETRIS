"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from Parser import Parser, C_ARITHMETIC, C_PUSH, C_POP, C_LABEL, C_GOTO, C_IF,\
    C_CALL, C_FUNCTION, C_RETURN
from CodeWriter import CodeWriter

def translate_file(
        input_file: typing.TextIO,
        code_writer) -> None:
    """Translates a single file.

    Args:
        input_file (typing.TextIO): the file to translate.
        output_file (typing.TextIO): writes all output to this file.
    """
    input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
    parser = Parser(input_file)

    code_writer.set_file_name(input_filename)
    while parser.has_more_commands():
        parser.advance()
        cur_cmd_type = parser.command_type()
        if cur_cmd_type == C_ARITHMETIC:
            code_writer.write_arithmetic(parser.arg1())
        if cur_cmd_type == C_PUSH or cur_cmd_type == C_POP:
            code_writer.write_push_pop(cur_cmd_type, parser.arg1(), parser.arg2())
        if cur_cmd_type == C_LABEL:
            code_writer.write_label(parser.arg1())
        if cur_cmd_type == C_IF:
            code_writer.write_if(parser.arg1())
        if cur_cmd_type == C_GOTO:
            code_writer.write_goto(parser.arg1())
        if cur_cmd_type == C_CALL:
            code_writer.write_call(parser.arg1(), parser.arg2())
        if cur_cmd_type == C_FUNCTION:
            code_writer.write_function(parser.arg1(), parser.arg2())
        if cur_cmd_type == C_RETURN:
            code_writer.write_return()



if __name__ == '__main__':
    # Parses the input path and calls translate_file on each input file
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: VMtranslator <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_translate = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
        output_path = os.path.join(argument_path, os.path.basename(
            argument_path))
    else:
        files_to_translate = [argument_path]
        output_path, extension = os.path.splitext(argument_path)
    output_path += ".asm"
    with open(output_path, 'w') as output_file:
        code_writer = CodeWriter(output_file)
        code_writer.write_init()
        for input_path in files_to_translate:
            filename, extension = os.path.splitext(input_path)
            if extension.lower() != ".vm":
                continue
            with open(input_path, 'r') as input_file:
                translate_file(input_file, code_writer)
