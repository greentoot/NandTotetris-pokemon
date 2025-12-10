import re
import sys
import Reader

class Lexer:
    """Analyseur lexical pour Jack"""

    def __init__(self, file):
        self.reader = Reader.Reader(file)
        self.tokens = [self._read(), self._read()]

    def _comment(self):
        """Gère les commentaires // et /* */"""
        t = self.reader.next()
        if self.reader.hasNext():
            t = self.reader.next()
        else:
            return None
        
        if t['char'] == '/':
            # Commentaire sur une ligne
            while t is not None and t['char'] != '\n':
                t = self.reader.next()
            return None
        elif t['char'] == '*':
            # Commentaire multi-lignes
            while True:
                while t is not None and t['char'] != '*':
                    t = self.reader.next()
                if t is None:
                    return None
                t = self.reader.next()
                if t is None or t['char'] == '/':
                    return None
        else:
            # Ce n'est pas un commentaire, c'est l'opérateur /
            self.reader.tokens_buffer = [t]  # Remettre le caractère dans le buffer
            return '/'

    def _skip(self):
        """Saute un caractère"""
        self.reader.next()
        return

    def _toke(self):
        """Lit un token (identifiant ou keyword)"""
        res = ''
        t = self.reader.look()
        while t is not None and re.fullmatch(r'[a-zA-Z0-9_]', t['char']):
            t = self.reader.next()
            res += t['char']
            t = self.reader.look()
        return res

    def _stringConstant(self):
        """Lit une chaîne de caractères"""
        res = '"'
        t = self.reader.next()
        if self.reader.hasNext():
            t = self.reader.next()
        else:
            return '""'
        while t is not None and t['char'] != '"':
            res += t['char']
            t = self.reader.next()
        return res + '"'

    def next(self):
        """Retourne le prochain token"""
        res = self.tokens[0]
        self.tokens[0] = self.tokens[1]
        self.tokens[1] = self._read()
        return res

    def _read(self):
        """Lit le prochain token depuis le Reader"""
        token = None
        while self.reader.hasNext() and token is None:
            self.line = self.reader._line
            self.col = self.reader._col
            t = self.reader.look()
            char = t['char']
            
            if char == '/':
                result = self._comment()
                if result is not None:
                    token = "/"
            elif char in '()[]{},.;=+-*&|~<>':
                token = char
                self._skip()
            elif char in ' \t\n':
                self._skip()
            elif re.fullmatch(r'[a-zA-Z0-9_]', char):
                token = self._toke()
            elif char == '"':
                token = self._stringConstant()
            else:
                print(f'SyntaxError : line={self.line}, col={self.col}, char="{char}"')
                exit()

        if token is None:
            return None
        else:
            pattern = self._pattern()
            group = pattern.fullmatch(token)
            if group is None:
                print(f'SyntaxError (line={self.line}, col={self.col}): {token}')
                exit()
            else:
                return {'line': self.line, 'col': self.col, 'type': group.lastgroup, 'token': token}

    def hasNext(self):
        """Vérifie si un token est disponible"""
        return self.tokens[0] is not None

    def hasNext2(self):
        """Vérifie si deux tokens sont disponibles"""
        return self.tokens[1] is not None

    def look(self):
        """Regarde le prochain token sans le consommer"""
        return self.tokens[0]

    def look2(self):
        """Regarde le token suivant sans le consommer"""
        return self.tokens[1]

    def _pattern(self):
        """Pattern regex pour identifier les types de tokens"""
        return re.compile(r"""
            (?P<symbol>[()[\]{},;=.+\-*/&|~<>])|
            (?P<keyword>class|constructor|method|function|int|boolean|char|void|var|static|field|let|do|if|else|while|return|true|false|null|this)|
            (?P<identifier>[a-zA-Z_][a-zA-Z0-9_]*)|
            (?P<StringConstant>\"[^\n]*\")|
            (?P<IntegerConstant>[0-9]+)
        """, re.X)

    def __iter__(self):
        return self

    def __next__(self):
        if self.hasNext():
            return self.next()
        else:
            raise StopIteration


if __name__ == "__main__":
    file = sys.argv[1]
    print('-----debut')
    lexer = Lexer(file)
    for token in lexer:
        print(token)
    print('-----fin')