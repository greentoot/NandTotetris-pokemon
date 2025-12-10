import tkinter as tk
from tkinter import filedialog
import json

ROWS = 16
COLS = 32
CELL_SIZE = 25   # Taille des cases

class MatrixEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Éditeur matrice 32x16 (0 à 49)")

        self.current_value = 0
        self.mouse_down = False  # Pour dessiner en continu

        # Matrice interne
        self.matrix = [[0 for _ in range(COLS)] for _ in range(ROWS)]

        # --- Sélecteur de valeurs (0 à 49) ---
        frame_buttons = tk.Frame(root)
        frame_buttons.pack(pady=5)

        tk.Label(frame_buttons, text="Valeur : ").pack(side=tk.LEFT)

        for i in range(50):
            b = tk.Button(frame_buttons, text=str(i), width=3,
                          command=lambda v=i: self.set_value(v))
            b.pack(side=tk.LEFT, padx=1)

        # --- Canvas ---
        self.canvas = tk.Canvas(root,
                                width=COLS * CELL_SIZE,
                                height=ROWS * CELL_SIZE,
                                bg="white")
        self.canvas.pack()

        # Événements souris
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)

        # Légendes (optionnelles, manquantes = pas grave)
        self.LEGENDS = [
            "Chemin", "Grass", "Water", "Tree", "PokeCenter", "Maison1", "Maisons2",
            "Parquet", "Wall1", "Wall2", "table_pokeball_droite", "table_pokeball_gauche",
            "table_pokeball_milieu", "Wall3", "Wall4", "Wall5", "Void", "pokeballsauvage",
            "Carrelage", "longburreaux", "Sapin", "etagere", "incubateur",
            "Bridge1", "Bridge2", "Bridge3", "Tabouret", "Parquet2",
        ] + [""]*(50-28)

        self.draw_grid()

        # --- Buttons Export / Import ---
        frame_io = tk.Frame(root)
        frame_io.pack(pady=10)

        tk.Button(frame_io, text="Importer map", command=self.import_matrix).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_io, text="Exporter map", command=self.export_matrix).pack(side=tk.LEFT, padx=5)

    def set_value(self, v):
        self.current_value = v

    def on_mouse_down(self, event):
        self.mouse_down = True
        self.apply_draw(event)

    def on_mouse_up(self, event):
        self.mouse_down = False

    def on_mouse_move(self, event):
        if self.mouse_down:
            self.apply_draw(event)

    def apply_draw(self, event):
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE

        if 0 <= col < COLS and 0 <= row < ROWS:
            self.matrix[row][col] = self.current_value
            self.draw_cell(row, col)

    def draw_grid(self):
        for r in range(ROWS):
            for c in range(COLS):
                self.draw_cell(r, c)

    def draw_cell(self, r, c):
        x1 = c * CELL_SIZE
        y1 = r * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE

        value = self.matrix[r][c]

        # Générer 50 couleurs automatiques
        colors = [
            "#eeeeee","#ffaaaa","#aaffaa","#aaaaff","#ffffaa","#ffaaff","#aaffff","#dddddd",
            "#ffccaa","#ccffaa","#aaccff","#ffaad4","#d4aaff","#aaffd4","#ffd4aa","#ccddee",
            "#eeddcc","#ddffaa","#ccddaa","#ddccaa","#ccaadd","#aaddcc","#ddaacc","#aaccdd",
            "#ccccaa","#aaccaa","#ccaacc","#aaccbb","#ddaaaa","#aaddaa","#aaaadd","#ddaadd",
            "#ddccdd","#ccddee","#eeccdd","#ddeecc","#eeddee","#eeddcc","#ccbbaa","#bbccaa",
            "#aabbcc","#ccaabb","#bbccdd","#ddbbcc","#ccddbb","#eeccaa","#aaccbb","#bbaacc","#ccaadd","#ddaacc"
        ]
        color = colors[value % len(colors)]

        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=color,
            outline="black"
        )

        # Légende optionnelle : si absente -> afficher juste le numéro
        legend = self.LEGENDS[value] if value < len(self.LEGENDS) and self.LEGENDS[value] else str(value)

        self.canvas.create_text(
            x1 + CELL_SIZE//2,
            y1 + CELL_SIZE//2,
            text=legend,
            font=("Arial", 7),
            fill="black"
        )

    # -------- IMPORT ----------
    def import_matrix(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json")]
        )
        if not filename:
            return

        with open(filename, "r") as f:
            content = f.read().strip()

        # ---- Import JSON ----
        if content.startswith("["):
            try:
                self.matrix = json.loads(content)
                print("Import JSON détecté :", filename)
                self.draw_grid()
                return
            except:
                pass

        # ---- Import format do setRow(...) ----
        lines = content.splitlines()
        parsed_matrix = []

        for line in lines:
            line = line.strip()

            if line.startswith("do setRow(") and line.endswith(");"):
                inner = line[len("do setRow("):-2]
                row_id_str, values_str = inner.split(",", 1)
                values = [int(v.strip()) for v in values_str.split(",")]
                parsed_matrix.append(values)

        if len(parsed_matrix) == ROWS and all(len(r) == COLS for r in parsed_matrix):
            self.matrix = parsed_matrix
            print("Import setRow détecté :", filename)
            self.draw_grid()
        else:
            print("Erreur : format fichier invalide.")

    # -------- EXPORT ----------
    def export_matrix(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )
        if not filename:
            return

        # Export JSON
        with open(filename, "w") as f:
            f.write(json.dumps(self.matrix))

        print("Matrice exportée :", filename)

        # Export Jack
        jack_lines = []
        for row_index, row in enumerate(self.matrix):
            line = f"do setRow({row_index}, " + ",".join(str(v) for v in row) + ");"
            jack_lines.append(line)

        jack_filename = filename.replace(".txt", "_setrow.jack")
        with open(jack_filename, "w") as jf:
            jf.write("\n".join(jack_lines))

        print("Code Jack généré :", jack_filename)


root = tk.Tk()
app = MatrixEditor(root)
root.mainloop()
