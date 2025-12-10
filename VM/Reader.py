import os
import sys


class Reader:
    """Lecteur de caractères pour fichiers VM"""

    def __init__(self, file):
        self.char = None
        self._line = 1
        self._col = 1
        self.file = None
        
        if os.path.exists(file):
            self.file = open(file, "r")
            self.char = self.file.read(1)
        else:
            print(f"Erreur: le fichier {file} n'existe pas")
            exit()

    def look(self):
        """Regarde le caractère courant sans le consommer"""
        if self.char:
            return {'line': self._line, 'col': self._col, 'char': self.char}
        return None

    def next(self):
        """Retourne le caractère courant et avance au suivant"""
        if not self.char:
            return None
        
        res = {'line': self._line, 'col': self._col, 'char': self.char}
        
        if self.hasNext():
            if self.char == '\n':
                self._line += 1
                self._col = 1
            else:
                self._col += 1
            
            self.char = self.file.read(1)
            
            if not self.char:  # Fin de fichier
                if self.file:
                    self.file.close()
                    self.file = None
        else:
            self.char = None
        
        return res

    def hasNext(self):
        """Vérifie s'il y a encore des caractères à lire"""
        return self.char is not None and len(self.char) > 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.hasNext():
            return self.next()
        else:
            raise StopIteration

    def __del__(self):
        """Ferme le fichier proprement"""
        if self.file:
            self.file.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python Reader.py <file>")
        sys.exit(1)
    
    file = sys.argv[1]
    print('-----debut')
    reader = Reader(file)
    for c in reader:
        print(c)
    print('-----fin')