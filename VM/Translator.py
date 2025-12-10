import os
import glob
import sys
import Generator


class Translator:
    """Traduit des fichiers VM en Assembly Hack"""

    def __init__(self, files, asm):
        self.asm = open(asm, "w")
        self.files = files

    def translate(self):
        """Écrit le bootstrap, puis traduit chaque fichier VM en assembly"""
        self.asm.write(self._bootstrap())
        
        if os.path.isfile(self.files):
            # Un seul fichier
            self._translateonefile(self.files)
        elif os.path.isdir(self.files):
            # Un répertoire de fichiers
            vm_files = glob.glob(os.path.join(self.files, '*.vm'))
            # Trier pour avoir Sys.vm en premier si présent
            vm_files.sort(key=lambda x: (not x.endswith('Sys.vm'), x))
            for file in vm_files:
                self._translateonefile(file)
        else:
            print(f"Erreur: {self.files} n'est ni un fichier ni un répertoire")
            exit()
        
        self.asm.close()

    def _translateonefile(self, file):
        """Traduit un seul fichier VM"""
        self.asm.write(f"\n// ========== {os.path.basename(file)} ==========\n")
        generator = Generator.Generator(file)
        for command in generator:
            if command:
                self.asm.write(command)

    def _bootstrap(self):
        """Code de bootstrap pour initialiser la VM"""
        # Créer un générateur temporaire pour générer l'appel à Sys.init
        temp_gen = Generator.Generator()
        temp_gen.filename = "Bootstrap"
        init_call = temp_gen._commandcall({
            'type': 'call',
            'function': 'Sys.init',
            'parameter': '0'
        })

        return f"""// Bootstrap
@256
D=A
@SP
M=D
{init_call}"""


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python Translator.py <vm_file|directory> <asm_file>")
        print("Example: python Translator.py SimpleAdd.vm SimpleAdd.asm")
        print("Example: python Translator.py MyProject/ MyProject.asm")
        sys.exit(1)
    
    vmfiles = sys.argv[1]
    asmfile = sys.argv[2]
    translator = Translator(vmfiles, asmfile)
    translator.translate()
    print(f"Traduction terminée: {asmfile}")