import sys

INSTRUCTION_LEN = 15
COMP_DICT = {
    '0': '0101010',
    '1': '0111111',
    '-1': '0111010',
    'D': '0001100',
    'A': '0110000',
    '!D': '0001101',
    '!A': '0110001',
    '-D': '0001111',
    '-A': '0110011',
    'D+1': '0011111',
    'A+1': '0110111',
    'D-1': '0001110',
    'A-1': '0110010',
    'D+A': '0000010',
    'D-A': '0010011',
    'A-D': '0000111',
    'D&A': '0000000',
    'D|A': '0010101',
    'M': '1110000',
    '!M': '1110001',
    '-M': '1110011',
    'M+1': '1110111',
    'M-1': '1110010',
    'D+M': '1000010',
    'D-M': '1010011',
    'M-D': '1000111',
    'D&M': '1000000',
    'D|M': '1010101'
}

DEST_DICT = {
    '':'000',
    'M':'001',
    'D':'010',
    'MD':'011',
    'A':'100',
    'AM':'101',
    'AD':'110',
    'AMD':'111'
}

JUMP_DICT = {
    '': '000',
    'JGT': '001',
    'JEQ': '010',
    'JGE': '011',
    'JLT': '100',
    'JNE': '101',
    'JLE': '110',
    'JMP': '111'
}

BUILTIN_SYMBOLS = { "SCREEN":'16384',
                   "KBD":'24576',
                   "SP":'0',
                   "LCL":'1',
                   "ARG":'2',
                   "THIS":'3',
                   "THAT":'4',
                   "R0":'0',
                   "R1":'1',
                   "R2":'2',
                   "R3":'3',
                   "R4":'4',
                   "R5":'5',
                   "R6":'6',
                   "R7":'7',
                   "R8":'8',
                   "R9":'9',
                   "R10":'10',
                   "R11":'11',
                   "R12":'12',
                    "R13":'13',
                   "R14":'14',
                   "R15":'15',
                }

def isAInstruction(instruction):
    return instruction.startswith('@')

def translateAInstruction(instruction):
    binary = str(bin(int(instruction[1:]))[2:])

    zeros_num = INSTRUCTION_LEN - len(binary) + 1
    zeros = '0'*zeros_num

    return zeros + binary + '\n'


def translateCInstruction(instruction):
    # dest = comp ;jump

    if "=" in instruction:
        [dest, comp_and_jump] = instruction.split("=")
        if (';' in comp_and_jump):
            [comp, jump] = comp_and_jump(';')
        else: 
            comp = comp_and_jump
            jump = ''

    else:
        [comp, jump] = instruction.split(';')
        dest = ''

    return str(111) + COMP_DICT[comp] + DEST_DICT[dest] + JUMP_DICT[jump] + '\n'

def createMatchingHackFile(asm_file_path):
    hack_file_name = asm_file_path[:asm_file_path.index('asm')] + 'hack'
    return open(hack_file_name, 'w+')
    
def simple_assembler(lines, hack_file):
    for line in lines:
        if isAInstruction(line):
            translatedLine = translateAInstruction(line)
        else:
            translatedLine = translateCInstruction(line)
        hack_file.write(translatedLine)

def remove_newline_char(string):
    return string.split('\n')[0]

def remove_inline_comments(string):
    return string.split('//')[0]

def clean_lines(lines):
    new_lines = []
    for line in lines:
        clean_line = line.replace(' ', '')
        if clean_line == '\n' or clean_line.startswith("//"):
            continue

        new_lines.append(
            remove_newline_char(
                remove_inline_comments(clean_line)
                )
            )
    
    return new_lines


def symbols_parser(lines):
    lines_without_label_dec = []
    symbols_table = BUILTIN_SYMBOLS
    # first parse: put in symbols table lines that start with: (, 
    # and delete them |||| (LOOP) > { LOOP: <next_line_idx>}
    i = 0
    for line in lines:
        if line.startswith('('): # label
            start_idx = line.index('(') + 1
            end_idx = line.index(')')
            label = line[start_idx:end_idx]
            symbols_table[label] = str(i)
        else: # not a label
            lines_without_label_dec.append(line)
            i += 1

    # second parse: every place with @_ s.t _ is in the sybols table 
    # - replace with matching number @LOOP > @<next_line_idx>

    lines_without_labels = []

    for line in lines_without_label_dec:
        line_to_add = line
        if line.startswith('@'):
            cur_loc_symbol = line[1:]
            if cur_loc_symbol in symbols_table.keys():
                line_to_add = '@' + symbols_table[cur_loc_symbol]
        lines_without_labels.append(line_to_add)

    # third parse: every place with @_ s.t _ is not a number 
    # - add to symbols table || @i >  { i: 16 }

    lines_without_symbols = []

    location_counter = 16
    for line in lines_without_labels:
        line_to_add = line
        if line.startswith('@') \
          and not line[1:].isdigit(): # this is a variable
            var = line[1:]
            if var not in symbols_table.keys():
                symbols_table[var] = str(location_counter)
                location_counter += 1

            line_to_add = '@' + symbols_table[var]

        lines_without_symbols.append(line_to_add)
    
    return lines_without_symbols


def parse_file(file_path):
    hack_file = createMatchingHackFile(file_path)
    with open(file_path, 'r') as asm_file:
        lines = asm_file.readlines()
        simple_assembler(symbols_parser(clean_lines(lines)), hack_file)
    
    hack_file.close()


def main():
    paths = sys.argv[1:]
    for path in paths:
        parse_file(path)
    
    return 0

if __name__ == "__main__":
    main()
