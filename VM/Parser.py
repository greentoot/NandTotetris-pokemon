import sys
import Lexer


class Parser:
    """Parser pour fichiers VM"""

    def __init__(self, file):
        self.lexer = Lexer.Lexer(file)
        self.command = self._read()

    def next(self):
        """Retourne la prochaine commande"""
        res = self.command
        self.command = self._read()
        return res

    def look(self):
        """Regarde la prochaine commande sans la consommer"""
        return self.command

    def hasNext(self):
        """Vérifie si une commande est disponible"""
        return self.command is not None

    def __iter__(self):
        return self

    def __next__(self):
        if self.hasNext():
            return self.next()
        else:
            raise StopIteration

    def _read(self):
        """Lit la prochaine commande depuis le Lexer"""
        command = self.lexer.look()
        if command is None:
            return None
        
        cmd_type = command['type']
        
        if cmd_type == 'pushpop':
            return self._commandpushpop()
        elif cmd_type == 'branching':
            return self._commandbranching()
        elif cmd_type == 'arithmetic':
            return self._commandarithmetic()
        elif cmd_type == 'function':
            return self._commandfunction()
        elif cmd_type == 'return':
            return self._commandreturn()
        else:
            print(f'SyntaxError : unexpected token type {cmd_type}: {command}')
            exit()

    def _commandarithmetic(self):
        """Parse une commande arithmétique (add, sub, neg, eq, gt, lt, and, or, not)"""
        command = self.lexer.next()
        return {
            'line': command['line'],
            'col': command['col'],
            'type': command['token']
        }

    def _commandpushpop(self):
        """Parse une commande push/pop"""
        command = self.lexer.next()
        segment = self.lexer.next()
        parameter = self.lexer.next()
        
        if segment is None or parameter is None:
            print(f"SyntaxError (line={command['line']}, col={command['col']}): incomplete {command['token']} command")
            exit()
        
        if segment['type'] != 'segment':
            print(f"SyntaxError (line={command['line']}, col={command['col']}): expected segment, got {segment['type']}")
            exit()
        
        if parameter['type'] != 'int':
            print(f"SyntaxError (line={command['line']}, col={command['col']}): expected integer, got {parameter['type']}")
            exit()

        return {
            'line': command['line'],
            'col': command['col'],
            'type': command['token'],
            'segment': segment['token'],
            'parameter': parameter['token']
        }

    def _commandbranching(self):
        """Parse une commande de branchement (label, goto, if-goto)"""
        command = self.lexer.next()
        label = self.lexer.next()
        
        if label is None:
            print(f"SyntaxError (line={command['line']}, col={command['col']}): missing label")
            exit()
        
        if label['type'] not in ('string', 'int'):
            print(f"SyntaxError (line={command['line']}, col={command['col']}): expected label name")
            exit()

        return {
            'line': command['line'],
            'col': command['col'],
            'type': command['token'],
            'label': label['token']
        }

    def _commandfunction(self):
        """Parse une commande function ou call"""
        command = self.lexer.next()
        name = self.lexer.next()
        parameter = self.lexer.next()
        
        if name is None or parameter is None:
            print(f"SyntaxError (line={command['line']}, col={command['col']}): incomplete {command['token']} command")
            exit()
        
        if name['type'] != 'string':
            print(f"SyntaxError (line={command['line']}, col={command['col']}): expected function name")
            exit()
        
        if parameter['type'] != 'int':
            print(f"SyntaxError (line={command['line']}, col={command['col']}): expected integer")
            exit()

        return {
            'line': command['line'],
            'col': command['col'],
            'type': command['token'],
            'function': name['token'],
            'parameter': parameter['token']
        }

    def _commandreturn(self):
        """Parse une commande return"""
        command = self.lexer.next()
        return {
            'line': command['line'],
            'col': command['col'],
            'type': command['token']
        }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python Parser.py <file.vm>")
        sys.exit(1)
    file = sys.argv[1]
    print('-----debut')
    parser = Parser(file)
    for command in parser:
        print(command)
    print('-----fin')