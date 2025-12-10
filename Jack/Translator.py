import os
import glob
import sys
import Generator


class Translator:
    def __init__(self, files):
        self.files = files
        self.all_vm_outputs = {}  # filename -> vm code

    def translate(self):
        if os.path.isfile(self.files):
            self._translate_one_file(self.files)
        elif os.path.isdir(self.files):
            for file in glob.glob(f'{self.files}/*.jack'):
                self._translate_one_file(file)
        else:
            print("Erreur : chemin invalide.")
            return

        # Après avoir traduit tous les fichiers : créer final.vm
        self._write_final_vm()

    def _translate_one_file(self, file):
        print(f"--- Traduction de {file} ---")
        generator = Generator.Generator(file)
        generator.generate()  # génère le code VM
        vm_code = "\n".join(generator.vm_lines)

        out = file.replace(".jack", ".vm")
        with open(out, "w") as f:
            f.write(vm_code)
        print(f"Fichier VM généré : {out}")

        # Stocke pour final.vm
        filename_only = os.path.basename(out)
        self.all_vm_outputs[filename_only] = vm_code

    def _write_final_vm(self):
        if not self.all_vm_outputs:
            print("Aucun fichier VM à assembler dans final.vm")
            return

        # Trie : met Main.vm en premier si présent
        ordered_files = sorted(
            self.all_vm_outputs.keys(),
            key=lambda name: (0 if name.lower().startswith("main") else 1, name)
        )

        final_code = ""

        for fname in ordered_files:
            final_code += f"// -------- {fname} --------\n"
            final_code += self.all_vm_outputs[fname] + "\n\n"

        output_path = (
            os.path.join(self.files, "final.vm")
            if os.path.isdir(self.files)
            else "final.vm"
        )

        with open(output_path, "w") as f:
            f.write(final_code)

        print(f"\nFichier assemblé généré : {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: Translator.py <fichier.jack | dossier>")
        sys.exit(1)

    path = sys.argv[1]
    translator = Translator(path)
    translator.translate()
