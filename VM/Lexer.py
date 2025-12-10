import re
import sys
import Reader

class Lexer:
    """Analyseur lexical pour fichiers VM"""

    def __init__(self, file):
        self.reader = Reader.Reader(file)
        self.tokens = [self._read(), self._read()]

    def _skip_whitespace_and_comments(self):
        """Saute les espaces et commentaires"""
        while self.reader.hasNext():
            t = self.reader.look()
            if t is None:
                break
            
            char = t['char']
            
            # Espaces blancs
            if char in ' \t\n\r':
                self.reader.next()
                continue
            
            # Commentaires //
            if char == '/':
                self.reader.next()
                if self.reader.hasNext():
                    next_char = self.reader.look()
                    if next_char and next_char['char'] == '/':
                        # Commentaire sur une ligne
                        while self.reader.hasNext():
                            c = self.reader.next()
                            if c['char'] == '\n':
                                break
                        continue
                    else:
                        # Ce n'est pas un commentaire, remettre le /
                        # dans VM il n'y a pas d'opérateur /
                        pass
                break
            else:
                break

    def _read_token(self):
        """Lit un token (mot ou nombre)"""
        res = ''
        while self.reader.hasNext():
            t = self.reader.look()
            if t is None:
                break
            char = t['char']
            # Token = lettres, chiffres, tirets, points, underscore
            if re.match(r'[a-zA-Z0-9_.\-]', char):
                res += char
                self.reader.next()
            else:
                break
        return res

    def next(self):
        """Retourne le prochain token"""
        res = self.tokens[0]
        self.tokens[0] = self.tokens[1]
        self.tokens[1] = self._read()
        return res

    def _read(self):
        """Lit le prochain token depuis le Reader"""
        self._skip_whitespace_and_comments()
        
        if not self.reader.hasNext():
            return None
        
        self.line = self.reader._line
        self.col = self.reader._col
        
        token = self._read_token()
        
        if not token:
            return None
        
        # Déterminer le type de token
        token_type = self._classify_token(token)
        
        return {
            'line': self.line,
            'col': self.col,
            'type': token_type,
            'token': token
        }

    def _classify_token(self, token):
        """Classifie le type de token"""
        # Commandes push/pop
        if token in ('push', 'pop'):
            return 'pushpop'
        
        # Commandes arithmétiques et logiques
        if token in ('add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not'):
            return 'arithmetic'
        
        # Commandes de branchement
        if token in ('label', 'goto', 'if-goto'):
            return 'branching'
        
        # Commandes de fonction
        if token in ('function', 'call'):
            return 'function'
        
        # Commande return
        if token == 'return':
            return 'return'
        
        # Segments mémoire
        if token in ('local', 'argument', 'this', 'that', 'constant', 'static', 'pointer', 'temp'):
            return 'segment'
        
        # Nombre entier
        if re.fullmatch(r'\d+', token):
            return 'int'
        
        # Chaîne (nom de fonction, label, etc.)
        if re.fullmatch(r'[a-zA-Z_][a-zA-Z0-9_.\-:$]*', token):
            return 'string'
        
        # Par défaut
        return 'unknown'

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

    def __iter__(self):
        return self

    def __next__(self):
        if self.hasNext():
            return self.next()
        else:
            raise StopIteration


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python Lexer.py <file.vm>")
        sys.exit(1)
    file = sys.argv[1]
    print('-----debut')
    lexer = Lexer(file)
    for token in lexer:
        print(token)
    print('-----fin')