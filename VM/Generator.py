import sys
import os
import Parser

class Generator:
    label_counter = 0  # Compteur global pour labels uniques

    """VM to Hack Assembly generator"""

    def __init__(self, file=None):
        self.parser = None
        self.current_function = "null"
        self.filename = None
        if file is not None:
            self.parser = Parser.Parser(file)
            # Conserver le nom de fichier (sans extension) pour les static
            self.filename = os.path.splitext(os.path.basename(file))[0]

    def __iter__(self):
        return self

    def __next__(self):
        if self.parser is not None and self.parser.hasNext():
            return self._next()
        else:
            raise StopIteration

    def _next(self):
        command = self.parser.next()
        if command is None:
            return None
        
        ctype = command.get('type', '').lower()

        if ctype in ('push', 'pop'):
            return self._commandpushpop(command)
        elif ctype in ('add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not'):
            return self._commandarith(command)
        elif ctype == 'call':
            return self._commandcall(command)
        elif ctype == 'return':
            return self._commandreturn(command)
        elif ctype == 'function':
            return self._commandfunction(command)
        elif ctype == 'label':
            return self._commandlabel(command)
        elif ctype == 'goto':
            return self._commandgoto(command)
        elif ctype == 'if-goto':
            return self._commandif(command)
        else:
            print(f'SyntaxError : unknown command type: {command}')
            exit()

    # ---------------- PUSH/POP ----------------
    def _commandpushpop(self, command):
        ctype = command['type'].lower()
        segment = command['segment']
        index = int(command['parameter'])

        if ctype == 'push':
            return self._push(segment, index)
        else:
            return self._pop(segment, index)

    def _push(self, segment, index):
        if segment == 'constant':
            return f"""// push constant {index}
@{index}
D=A
@SP
A=M
M=D
@SP
M=M+1
"""
        elif segment in ('local', 'argument', 'this', 'that'):
            seg_map = {'local': 'LCL', 'argument': 'ARG', 'this': 'THIS', 'that': 'THAT'}
            seg_name = seg_map[segment]
            return f"""// push {segment} {index}
@{seg_name}
D=M
@{index}
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
"""
        elif segment == 'temp':
            return f"""// push temp {index}
@{5 + index}
D=M
@SP
A=M
M=D
@SP
M=M+1
"""
        elif segment == 'pointer':
            ptr = 'THIS' if index == 0 else 'THAT'
            return f"""// push pointer {index}
@{ptr}
D=M
@SP
A=M
M=D
@SP
M=M+1
"""
        elif segment == 'static':
            return f"""// push static {index}
@{self.filename}.{index}
D=M
@SP
A=M
M=D
@SP
M=M+1
"""

    def _pop(self, segment, index):
        if segment in ('local', 'argument', 'this', 'that'):
            seg_map = {'local': 'LCL', 'argument': 'ARG', 'this': 'THIS', 'that': 'THAT'}
            seg_name = seg_map[segment]
            return f"""// pop {segment} {index}
@{seg_name}
D=M
@{index}
D=D+A
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
"""
        elif segment == 'temp':
            return f"""// pop temp {index}
@SP
AM=M-1
D=M
@{5 + index}
M=D
"""
        elif segment == 'pointer':
            ptr = 'THIS' if index == 0 else 'THAT'
            return f"""// pop pointer {index}
@SP
AM=M-1
D=M
@{ptr}
M=D
"""
        elif segment == 'static':
            return f"""// pop static {index}
@SP
AM=M-1
D=M
@{self.filename}.{index}
M=D
"""

    # ---------------- ARITHMETIC ----------------
    def _commandarith(self, command):
        ctype = command['type'].lower()
        
        if ctype == 'add':
            return """// add
@SP
AM=M-1
D=M
A=A-1
M=D+M
"""
        elif ctype == 'sub':
            return """// sub
@SP
AM=M-1
D=M
A=A-1
M=M-D
"""
        elif ctype == 'neg':
            return """// neg
@SP
A=M-1
M=-M
"""
        elif ctype == 'and':
            return """// and
@SP
AM=M-1
D=M
A=A-1
M=D&M
"""
        elif ctype == 'or':
            return """// or
@SP
AM=M-1
D=M
A=A-1
M=D|M
"""
        elif ctype == 'not':
            return """// not
@SP
A=M-1
M=!M
"""
        elif ctype in ('eq', 'gt', 'lt'):
            lab_true = f"TRUE_{Generator.label_counter}"
            lab_end = f"END_{Generator.label_counter}"
            Generator.label_counter += 1
            jump_map = {'eq': 'JEQ', 'gt': 'JGT', 'lt': 'JLT'}
            jump = jump_map[ctype]
            return f"""// {ctype}
@SP
AM=M-1
D=M
A=A-1
D=M-D
@{lab_true}
D;{jump}
@SP
A=M-1
M=0
@{lab_end}
0;JMP
({lab_true})
@SP
A=M-1
M=-1
({lab_end})
"""

    # ---------------- CALL ----------------
    def _commandcall(self, command):
        func = command.get('function', command.get('functionName'))
        nargs = int(command.get('parameter', 0))

        ret_label = f"RETURN_{Generator.label_counter}"
        Generator.label_counter += 1
        
        return f"""// call {func} {nargs}
@{ret_label}
D=A
@SP
A=M
M=D
@SP
M=M+1
@LCL
D=M
@SP
A=M
M=D
@SP
M=M+1
@ARG
D=M
@SP
A=M
M=D
@SP
M=M+1
@THIS
D=M
@SP
A=M
M=D
@SP
M=M+1
@THAT
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
D=M
@{nargs}
D=D-A
@5
D=D-A
@ARG
M=D
@SP
D=M
@LCL
M=D
@{func}
0;JMP
({ret_label})
"""

    # ---------------- FUNCTION ----------------
    def _commandfunction(self, command):
        name = command.get('function', command.get('functionName'))
        nlocals = int(command.get('parameter', 0))

        self.current_function = name

        code = f"""// function {name} {nlocals}
({name})
"""
        # Initialiser les variables locales à 0
        for _ in range(nlocals):
            code += """@SP
A=M
M=0
@SP
M=M+1
"""
        return code

    # ---------------- RETURN ----------------
    def _commandreturn(self, command):
        return """// return
@LCL
D=M
@R13
M=D
@5
A=D-A
D=M
@R14
M=D
@SP
AM=M-1
D=M
@ARG
A=M
M=D
@ARG
D=M+1
@SP
M=D
@R13
AM=M-1
D=M
@THAT
M=D
@R13
AM=M-1
D=M
@THIS
M=D
@R13
AM=M-1
D=M
@ARG
M=D
@R13
AM=M-1
D=M
@LCL
M=D
@R14
A=M
0;JMP
"""

    # ---------------- BRANCHING ----------------
    def _prefix_label(self, label):
        """Préfixe le label avec le nom de la fonction courante"""
        return f"{self.current_function}${label}"

    def _commandlabel(self, command):
        label = self._prefix_label(command['label'])
        return f"""// label {command['label']}
({label})
"""

    def _commandgoto(self, command):
        label = self._prefix_label(command['label'])
        return f"""// goto {command['label']}
@{label}
0;JMP
"""

    def _commandif(self, command):
        label = self._prefix_label(command['label'])
        return f"""// if-goto {command['label']}
@SP
AM=M-1
D=M
@{label}
D;JNE
"""


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python Generator.py <file.vm>")
        sys.exit(1)
    file = sys.argv[1]
    print('-----debut')
    generator = Generator(file)
    for command in generator:
        print(command, end='')
    print('-----fin')