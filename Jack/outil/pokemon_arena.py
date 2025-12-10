import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, scrolledtext
import re

class PokemonArenaEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Éditeur d'Arène Pokémon")
        
        self.WIDTH = 160
        self.HEIGHT = 144
        self.CELL_SIZE = 4
        
        self.grid = [[0 for _ in range(self.WIDTH)] for _ in range(self.HEIGHT)]
        self.clipboard_grid = None
        self.draw_mode = 1
        self.is_drawing = False
        
        self.selection_mode = False 
        self.selection_start = None
        self.selection_end = None
        self.selected_region = None
        self.is_dragging_selection = False
        self.drag_offset = None
        
        # Variable pour indiquer si le code a été modifié depuis l'import
        self.grid_modified = False
        
        self.setup_ui()
        self.create_default_arena()
        self.draw_canvas()
    
    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(padx=10, pady=10)
        
        title = tk.Label(main_frame, text="Éditeur d'Arène Pokémon", 
                        font=('Arial', 16, 'bold'), bg='#f0f0f0')
        title.pack(pady=5)
        
        self.subtitle = tk.Label(main_frame, text=f"{self.WIDTH}×{self.HEIGHT} pixels", 
                           font=('Arial', 10), bg='#f0f0f0', fg='#666')
        self.subtitle.pack(pady=2)
        
        button_frame1 = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame1.pack(pady=5)
        
        self.draw_btn = tk.Button(button_frame1, text="✏️ Dessiner", 
                                  command=lambda: self.set_mode(1),
                                  bg='#3b82f6', fg='white', font=('Arial', 9, 'bold'),
                                  padx=12, pady=5)
        self.draw_btn.pack(side=tk.LEFT, padx=3)
        
        self.erase_btn = tk.Button(button_frame1, text="🗑️ Effacer", 
                                   command=lambda: self.set_mode(0),
                                   bg='#ef4444', fg='white', font=('Arial', 9, 'bold'),
                                   padx=12, pady=5)
        self.erase_btn.pack(side=tk.LEFT, padx=3)
        
        self.select_btn = tk.Button(button_frame1, text="🔲 Sélectionner", 
                                   command=self.toggle_selection_mode,
                                   bg='#f59e0b', fg='white', font=('Arial', 9, 'bold'),
                                   padx=12, pady=5)
        self.select_btn.pack(side=tk.LEFT, padx=3)
        
        clear_btn = tk.Button(button_frame1, text="🔄 Réinitialiser", 
                             command=self.clear_grid,
                             bg='#6b7280', fg='white', font=('Arial', 9, 'bold'),
                             padx=12, pady=5)
        clear_btn.pack(side=tk.LEFT, padx=3)
        
        button_frame2 = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame2.pack(pady=5)
        
        copy_btn = tk.Button(button_frame2, text="📋 Copier", 
                            command=self.copy_grid,
                            bg='#8b5cf6', fg='white', font=('Arial', 9, 'bold'),
                            padx=12, pady=5)
        copy_btn.pack(side=tk.LEFT, padx=3)
        
        paste_btn = tk.Button(button_frame2, text="📌 Coller", 
                             command=self.paste_grid,
                             bg='#8b5cf6', fg='white', font=('Arial', 9, 'bold'),
                             padx=12, pady=5)
        paste_btn.pack(side=tk.LEFT, padx=3)
        
        import_btn = tk.Button(button_frame2, text="📥 Importer code Jack", 
                              command=self.import_jack_code,
                              bg='#f59e0b', fg='white', font=('Arial', 9, 'bold'),
                              padx=12, pady=5)
        import_btn.pack(side=tk.LEFT, padx=3)
        
        export_btn = tk.Button(button_frame2, text="📤 Exporter code Jack", 
                              command=self.export_jack_code,
                              bg='#10b981', fg='white', font=('Arial', 9, 'bold'),
                              padx=12, pady=5)
        export_btn.pack(side=tk.LEFT, padx=3)
        
        save_btn = tk.Button(button_frame2, text="💾 Sauvegarder .jack", 
                            command=self.save_jack_code,
                            bg='#10b981', fg='white', font=('Arial', 9, 'bold'),
                            padx=12, pady=5)
        save_btn.pack(side=tk.LEFT, padx=3)
        
        size_frame = tk.Frame(main_frame, bg='#f0f0f0')
        size_frame.pack(pady=5)
        
        tk.Label(size_frame, text="Tailles:", 
                font=('Arial', 9, 'bold'), bg='#f0f0f0').pack(side=tk.LEFT, padx=5)
        
        presets = [
            ("32×16", 32, 16),
            ("64×32", 64, 32),
            ("160×144", 160, 144),
            ("256×64", 256, 64),
        ]
        
        for label, w, h in presets:
            btn = tk.Button(size_frame, text=label, 
                          command=lambda w=w, h=h: self.change_size(w, h),
                          bg='#06b6d4', fg='white', font=('Arial', 8),
                          padx=8, pady=3)
            btn.pack(side=tk.LEFT, padx=2)
        
        custom_btn = tk.Button(size_frame, text="✨ Personnalisée", 
                             command=self.custom_size,
                             bg='#f59e0b', fg='white', font=('Arial', 8, 'bold'),
                             padx=8, pady=3)
        custom_btn.pack(side=tk.LEFT, padx=5)
        
        resize_btn = tk.Button(size_frame, text="🔧 Redimensionner", 
                              command=self.resize_canvas,
                              bg='#ec4899', fg='white', font=('Arial', 8, 'bold'),
                              padx=8, pady=3)
        resize_btn.pack(side=tk.LEFT, padx=2)
        
        self.canvas_frame = tk.Frame(main_frame, bg='white', relief=tk.SUNKEN, borderwidth=3)
        self.canvas_frame.pack(pady=10)
        
        self.canvas = tk.Canvas(self.canvas_frame, 
                               width=self.WIDTH * self.CELL_SIZE,
                               height=self.HEIGHT * self.CELL_SIZE,
                               bg='white', highlightthickness=0)
        self.canvas.pack()
        
        self.canvas.bind('<Button-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.root.bind('<Escape>', lambda e: self.clear_selection())
        
        self.info_label = tk.Label(main_frame, 
                       text="Dessinez • Sélectionnez et déplacez des zones • Copiez/Collez • Importez du code Jack",
                       font=('Arial', 9), bg='#dbeafe', fg='#1e40af',
                       padx=10, pady=5, relief=tk.RIDGE)
        self.info_label.pack(pady=5)
    
    def mark_as_modified(self):
        """Marque la grille comme modifiée (pour régénération complète du code)"""
        self.grid_modified = True
    
    def set_mode(self, mode):
        self.draw_mode = mode
        self.selection_mode = False
        if mode == 1:
            self.draw_btn.config(relief=tk.SUNKEN)
            self.erase_btn.config(relief=tk.RAISED)
            self.select_btn.config(relief=tk.RAISED)
        else:
            self.draw_btn.config(relief=tk.RAISED)
            self.erase_btn.config(relief=tk.SUNKEN)
            self.select_btn.config(relief=tk.RAISED)
        self.clear_selection()
        self.update_info_text()
    
    def toggle_selection_mode(self):
        self.selection_mode = not self.selection_mode
        if self.selection_mode:
            self.draw_btn.config(relief=tk.RAISED)
            self.erase_btn.config(relief=tk.RAISED)
            self.select_btn.config(relief=tk.SUNKEN)
        else:
            self.select_btn.config(relief=tk.RAISED)
        self.clear_selection()
        self.update_info_text()
    
    def update_info_text(self):
        if self.selection_mode:
            self.info_label.config(text="🔲 MODE SÉLECTION: Glissez pour sélectionner • Glissez la sélection pour déplacer • Échap pour annuler")
        elif self.draw_mode == 1:
            self.info_label.config(text="✏️ MODE DESSIN: Cliquez et glissez pour dessiner")
        else:
            self.info_label.config(text="🗑️ MODE EFFACER: Cliquez et glissez pour effacer")
    
    def clear_selection(self):
        self.selection_start = None
        self.selection_end = None
        self.selected_region = None
        self.is_dragging_selection = False
        self.draw_canvas()
    
    def copy_grid(self):
        self.clipboard_grid = [row[:] for row in self.grid]
        messagebox.showinfo("Copié", f"Grille {self.WIDTH}×{self.HEIGHT} copiée dans le presse-papier !")
    
    def paste_grid(self):
        if self.clipboard_grid is None:
            messagebox.showwarning("Aucune copie", "Aucune grille n'a été copiée !")
            return
        
        clipboard_h = len(self.clipboard_grid)
        clipboard_w = len(self.clipboard_grid[0]) if clipboard_h > 0 else 0
        
        if clipboard_w == self.WIDTH and clipboard_h == self.HEIGHT:
            self.grid = [row[:] for row in self.clipboard_grid]
            self.mark_as_modified()
            self.draw_canvas()
            messagebox.showinfo("Collé", "Grille collée avec succès !")
        else:
            msg = f"Grille copiée: {clipboard_w}×{clipboard_h}\n"
            msg += f"Grille actuelle: {self.WIDTH}×{self.HEIGHT}\n\n"
            msg += "Coller en haut à gauche ?"
            
            if messagebox.askyesno("Coller", msg):
                for y in range(min(clipboard_h, self.HEIGHT)):
                    for x in range(min(clipboard_w, self.WIDTH)):
                        self.grid[y][x] = self.clipboard_grid[y][x]
                self.mark_as_modified()
                self.draw_canvas()
                messagebox.showinfo("Collé", "Grille collée (partiellement si nécessaire) !")
    
    def resize_canvas(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Redimensionner le canvas")
        dialog.geometry("350x200")
        dialog.resizable(False, False)
        
        tk.Label(dialog, text="Nouvelle taille (votre dessin sera préservé):", 
                font=('Arial', 11, 'bold')).pack(pady=10)
        
        frame = tk.Frame(dialog)
        frame.pack(pady=10)
        
        tk.Label(frame, text="Largeur:", font=('Arial', 10)).grid(row=0, column=0, padx=5, pady=5)
        width_entry = tk.Entry(frame, width=10, font=('Arial', 10))
        width_entry.insert(0, str(self.WIDTH))
        width_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame, text="Hauteur:", font=('Arial', 10)).grid(row=1, column=0, padx=5, pady=5)
        height_entry = tk.Entry(frame, width=10, font=('Arial', 10))
        height_entry.insert(0, str(self.HEIGHT))
        height_entry.grid(row=1, column=1, padx=5, pady=5)
        
        def apply_resize():
            try:
                new_w = int(width_entry.get())
                new_h = int(height_entry.get())
                
                if new_w < 16 or new_h < 16:
                    messagebox.showerror("Erreur", "Taille minimale: 16×16 pixels")
                    return
                
                if new_w > 512 or new_h > 256:
                    messagebox.showerror("Erreur", "Taille maximale: 512×256 pixels")
                    return
                
                old_grid = [row[:] for row in self.grid]
                old_w, old_h = self.WIDTH, self.HEIGHT
                
                new_grid = [[0 for _ in range(new_w)] for _ in range(new_h)]
                
                for y in range(min(old_h, new_h)):
                    for x in range(min(old_w, new_w)):
                        new_grid[y][x] = old_grid[y][x]
                
                self.grid = new_grid
                self.WIDTH = new_w
                self.HEIGHT = new_h
                self.mark_as_modified()
                
                max_w, max_h = 800, 600
                cell_size_w = max_w // new_w
                cell_size_h = max_h // new_h
                self.CELL_SIZE = max(1, min(cell_size_w, cell_size_h, 10))
                
                self.subtitle.config(text=f"{self.WIDTH}×{self.HEIGHT} pixels")
                
                self.canvas.destroy()
                self.canvas = tk.Canvas(self.canvas_frame, 
                                       width=self.WIDTH * self.CELL_SIZE,
                                       height=self.HEIGHT * self.CELL_SIZE,
                                       bg='white', highlightthickness=0)
                self.canvas.pack()
                
                self.canvas.bind('<Button-1>', self.on_mouse_down)
                self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
                self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
                self.root.bind('<Escape>', lambda e: self.clear_selection())
                
                self.draw_canvas()
                dialog.destroy()
                messagebox.showinfo("Succès", "Canvas redimensionné avec préservation du dessin !")
                
            except ValueError:
                messagebox.showerror("Erreur", "Nombres invalides")
        
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="✓ Redimensionner", command=apply_resize,
                 bg='#10b981', fg='white', font=('Arial', 10, 'bold'),
                 padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="✗ Annuler", command=dialog.destroy,
                 bg='#6b7280', fg='white', font=('Arial', 10, 'bold'),
                 padx=20, pady=5).pack(side=tk.LEFT, padx=5)
    
    def import_jack_code(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Importer du code Jack")
        dialog.geometry("600x500")
        
        tk.Label(dialog, text="Collez votre code Jack ici:", 
                font=('Arial', 11, 'bold')).pack(pady=10)
        
        text_area = scrolledtext.ScrolledText(dialog, width=70, height=20, 
                                             font=('Courier', 9))
        text_area.pack(padx=10, pady=10)
        
        def parse_and_import():
            code = text_area.get('1.0', tk.END)
            
            pattern = r'Memory\.poke\(memAddress \+ (\d+),\s*(-?\d+)\)'
            matches = re.findall(pattern, code)
            
            if not matches:
                messagebox.showerror("Erreur", "Aucune instruction Memory.poke trouvée !")
                return
            
            # Vérifier si des offsets dépassent 32767
            max_offset_found = max(int(m[0]) for m in matches)
            has_invalid_offsets = max_offset_found > 32767
            
            if has_invalid_offsets:
                warning_msg = f"⚠️ ATTENTION : Le code contient des offsets invalides !\n\n"
                warning_msg += f"Offset maximum détecté : {max_offset_found}\n"
                warning_msg += f"Limite Jack : 32767\n\n"
                warning_msg += "L'éditeur va importer la grille et vous pourrez exporter un code corrigé.\n\n"
                warning_msg += "Continuer l'import ?"
                
                if not messagebox.askyesno("Offsets invalides détectés", warning_msg):
                    return
            
            max_offset = max(int(m[0]) for m in matches)
            
            estimated_height = (max_offset // 32) + 1
            estimated_width = 512
            
            temp_grid = [[0 for _ in range(estimated_width)] for _ in range(estimated_height)]
            
            for offset_str, value_str in matches:
                offset = int(offset_str)
                value = int(value_str)
                
                y = offset // 32
                word_idx = offset % 32
                
                if y >= estimated_height:
                    continue
                
                # Convertir la valeur signée en non-signée pour le traitement
                if value < 0:
                    value = value + 65536
                
                # Extraire les bits et les placer dans la grille
                for bit in range(16):
                    x = word_idx * 16 + bit
                    if x < estimated_width:
                        # bit 15 = position 0, bit 0 = position 15
                        if value & (1 << (15 - bit)):
                            temp_grid[y][x] = 1
            
            max_x = 0
            max_y = 0
            for y in range(estimated_height):
                for x in range(estimated_width):
                    if temp_grid[y][x] == 1:
                        max_x = max(max_x, x)
                        max_y = max(max_y, y)
            
            real_width = ((max_x // 16) + 1) * 16
            real_height = max_y + 1
            
            msg = f"Code détecté: {real_width}×{real_height} pixels\n"
            msg += f"Grille actuelle: {self.WIDTH}×{self.HEIGHT} pixels\n\n"
            
            if has_invalid_offsets:
                msg += "⚠️ Le code original contenait des offsets > 32767\n"
                msg += "✅ Un nouveau code valide sera généré à l'export\n\n"
            
            msg += "Options:\n"
            msg += "- OUI: Adapter la taille du canvas\n"
            msg += "- NON: Importer dans la taille actuelle"
            
            result = messagebox.askyesnocancel("Importer", msg)
            
            if result is None:
                return
            
            if result:
                self.WIDTH = real_width
                self.HEIGHT = real_height
                self.grid = [[0 for _ in range(self.WIDTH)] for _ in range(self.HEIGHT)]
                
                for y in range(min(real_height, self.HEIGHT)):
                    for x in range(min(real_width, self.WIDTH)):
                        self.grid[y][x] = temp_grid[y][x]
                
                max_w, max_h = 800, 600
                cell_size_w = max_w // self.WIDTH
                cell_size_h = max_h // self.HEIGHT
                self.CELL_SIZE = max(1, min(cell_size_w, cell_size_h, 10))
                
                self.subtitle.config(text=f"{self.WIDTH}×{self.HEIGHT} pixels")
                
                self.canvas.destroy()
                self.canvas = tk.Canvas(self.canvas_frame, 
                                       width=self.WIDTH * self.CELL_SIZE,
                                       height=self.HEIGHT * self.CELL_SIZE,
                                       bg='white', highlightthickness=0)
                self.canvas.pack()
                
                self.canvas.bind('<Button-1>', self.on_mouse_down)
                self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
                self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
            else:
                for y in range(min(real_height, self.HEIGHT)):
                    for x in range(min(real_width, self.WIDTH)):
                        self.grid[y][x] = temp_grid[y][x]
            
            # Marquer comme modifié pour forcer la régénération complète
            self.grid_modified = True
            
            self.draw_canvas()
            dialog.destroy()
            
            # Message de succès avec suggestion d'export
            success_msg = "Code Jack importé avec succès !"
            if has_invalid_offsets:
                success_msg += "\n\n⚠️ Le code original avait des offsets invalides."
                success_msg += "\n✅ Exportez maintenant pour générer un code corrigé et compatible !"
            
            messagebox.showinfo("Succès", success_msg)
        
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="✓ Importer", command=parse_and_import,
                 bg='#10b981', fg='white', font=('Arial', 10, 'bold'),
                 padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="✗ Annuler", command=dialog.destroy,
                 bg='#6b7280', fg='white', font=('Arial', 10, 'bold'),
                 padx=20, pady=5).pack(side=tk.LEFT, padx=5)
    
    def export_jack_code(self):
        code = self.generate_jack_code()
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Code Jack généré")
        dialog.geometry("700x500")
        
        tk.Label(dialog, text=f"Code Jack pour {self.WIDTH}×{self.HEIGHT} pixels:", 
                font=('Arial', 11, 'bold')).pack(pady=10)
        
        text_area = scrolledtext.ScrolledText(dialog, width=80, height=25, 
                                             font=('Courier', 9))
        text_area.pack(padx=10, pady=10)
        text_area.insert('1.0', code)
        text_area.config(state='disabled')
        
        def copy_to_clipboard():
            self.root.clipboard_clear()
            self.root.clipboard_append(code)
            messagebox.showinfo("Copié", "Code copié dans le presse-papier système !")
        
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="📋 Copier", command=copy_to_clipboard,
                 bg='#3b82f6', fg='white', font=('Arial', 10, 'bold'),
                 padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="✗ Fermer", command=dialog.destroy,
                 bg='#6b7280', fg='white', font=('Arial', 10, 'bold'),
                 padx=20, pady=5).pack(side=tk.LEFT, padx=5)
    
    def generate_jack_code(self):
        """Génère TOUJOURS un nouveau code Jack basé sur l'état actuel de la grille"""
        words_per_line = (self.WIDTH + 15) // 16
        total_pokes = self.HEIGHT * words_per_line
        
        MAX_POKES_PER_FUNCTION = 450
        
        if total_pokes <= MAX_POKES_PER_FUNCTION:
            return self._generate_single_function()
        else:
            return self._generate_split_functions(words_per_line, total_pokes)
    
    def _generate_single_function(self):
        """Génère une fonction unique à partir de l'état actuel de la grille"""
        code = "function void draw(int location) {\n"
        code += "    var int memAddress;\n"
        
        words_per_line = (self.WIDTH + 15) // 16
        
        # Vérifier si on a besoin de variables pour grands offsets
        max_offset = (self.HEIGHT - 1) * 32 + (words_per_line - 1)
        
        if max_offset > 32767:
            code += "    var int memAddress2;\n"
        
        code += "    let memAddress = 16384 + location;\n"
        
        if max_offset > 32767:
            code += "    let memAddress2 = memAddress + 32767;\n"
        
        code += "\n"
        
        for y in range(self.HEIGHT):
            for word_idx in range(words_per_line):
                val = 0
                start_x = word_idx * 16
                
                for bit in range(16):
                    x = start_x + bit
                    if x < self.WIDTH and self.grid[y][x] == 1:
                        val |= (1 << (15 - bit))
                
                # Conversion en entier signé 16-bit
                if val > 32767:
                    val = val - 65536
                
                offset = y * 32 + word_idx
                
                # Gérer les grands offsets
                if offset > 32767:
                    adjusted_offset = offset - 32767
                    code += f"    do Memory.poke(memAddress2 + {adjusted_offset}, {val});\n"
                else:
                    code += f"    do Memory.poke(memAddress + {offset}, {val});\n"
        
        code += "    return;\n"
        code += "}"
        
        return code
    
    def _generate_split_functions(self, words_per_line, total_pokes):
        """Génère plusieurs fonctions à partir de l'état actuel de la grille"""
        MAX_POKES = 450
        num_parts = (total_pokes + MAX_POKES - 1) // MAX_POKES
        
        code = "// Arène générée en plusieurs parties\n\n"
        
        code += "function void draw(int location) {\n"
        for i in range(num_parts):
            code += f"    do drawPart{i+1}(location);\n"
        code += "    return;\n"
        code += "}\n\n"
        
        # Vérifier si on a besoin de variables pour grands offsets
        max_offset = (self.HEIGHT - 1) * 32 + (words_per_line - 1)
        needs_offset_handling = max_offset > 32767
        
        poke_count = 0
        current_part = 1
        part_code = f"function void drawPart{current_part}(int location) {{\n"
        part_code += "    var int memAddress;\n"
        
        if needs_offset_handling:
            part_code += "    var int memAddress2;\n"
        
        part_code += "    let memAddress = 16384 + location;\n"
        
        if needs_offset_handling:
            part_code += "    let memAddress2 = memAddress + 32767;\n"
        
        part_code += "\n"
        
        for y in range(self.HEIGHT):
            for word_idx in range(words_per_line):
                val = 0
                start_x = word_idx * 16
                
                for bit in range(16):
                    x = start_x + bit
                    if x < self.WIDTH and self.grid[y][x] == 1:
                        val |= (1 << (15 - bit))
                
                if val > 32767:
                    val = val - 65536
                
                offset = y * 32 + word_idx
                
                # Gérer les grands offsets
                if offset > 32767:
                    adjusted_offset = offset - 32767
                    part_code += f"    do Memory.poke(memAddress2 + {adjusted_offset}, {val});\n"
                else:
                    part_code += f"    do Memory.poke(memAddress + {offset}, {val});\n"
                
                poke_count += 1
                
                if poke_count >= MAX_POKES and not (y == self.HEIGHT - 1 and word_idx == words_per_line - 1):
                    part_code += "    return;\n"
                    part_code += "}\n\n"
                    code += part_code
                    
                    current_part += 1
                    poke_count = 0
                    part_code = f"function void drawPart{current_part}(int location) {{\n"
                    part_code += "    var int memAddress;\n"
                    
                    if needs_offset_handling:
                        part_code += "    var int memAddress2;\n"
                    
                    part_code += "    let memAddress = 16384 + location;\n"
                    
                    if needs_offset_handling:
                        part_code += "    let memAddress2 = memAddress + 32767;\n"
                    
                    part_code += "\n"
        
        part_code += "    return;\n"
        part_code += "}\n"
        code += part_code
        
        return code
    
    def change_size(self, width, height):
        if messagebox.askyesno("Changer la taille", 
                              f"Changer en {width}×{height} pixels ?\nCela effacera le dessin actuel."):
            self.WIDTH = width
            self.HEIGHT = height
            
            max_w, max_h = 800, 600
            cell_size_w = max_w // width
            cell_size_h = max_h // height
            self.CELL_SIZE = max(1, min(cell_size_w, cell_size_h, 10))
            
            self.grid = [[0 for _ in range(self.WIDTH)] for _ in range(self.HEIGHT)]
            self.mark_as_modified()
            self.subtitle.config(text=f"{self.WIDTH}×{self.HEIGHT} pixels")
            
            self.canvas.destroy()
            self.canvas = tk.Canvas(self.canvas_frame, 
                                   width=self.WIDTH * self.CELL_SIZE,
                                   height=self.HEIGHT * self.CELL_SIZE,
                                   bg='white', highlightthickness=0)
            self.canvas.pack()
            
            self.canvas.bind('<Button-1>', self.on_mouse_down)
            self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
            self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
            self.root.bind('<Escape>', lambda e: self.clear_selection())
            
            if width >= 32 and height >= 16:
                self.create_simple_arena()
            
            self.draw_canvas()
    
    def custom_size(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Taille personnalisée")
        dialog.geometry("300x180")
        dialog.resizable(False, False)
        
        tk.Label(dialog, text="Entrez la taille de l'arène:", 
                font=('Arial', 11, 'bold')).pack(pady=10)
        
        frame = tk.Frame(dialog)
        frame.pack(pady=10)
        
        tk.Label(frame, text="Largeur:", font=('Arial', 10)).grid(row=0, column=0, padx=5, pady=5)
        width_entry = tk.Entry(frame, width=10, font=('Arial', 10))
        width_entry.insert(0, str(self.WIDTH))
        width_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(frame, text="pixels", font=('Arial', 9)).grid(row=0, column=2, padx=5)
        
        tk.Label(frame, text="Hauteur:", font=('Arial', 10)).grid(row=1, column=0, padx=5, pady=5)
        height_entry = tk.Entry(frame, width=10, font=('Arial', 10))
        height_entry.insert(0, str(self.HEIGHT))
        height_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(frame, text="pixels", font=('Arial', 9)).grid(row=1, column=2, padx=5)
        
        def apply_size():
            try:
                w = int(width_entry.get())
                h = int(height_entry.get())
                
                if w < 16 or h < 16:
                    messagebox.showerror("Erreur", "Taille minimale: 16×16 pixels")
                    return
                
                if w > 512 or h > 256:
                    messagebox.showerror("Erreur", "Taille maximale: 512×256 pixels")
                    return
                
                dialog.destroy()
                self.change_size(w, h)
            except ValueError:
                messagebox.showerror("Erreur", "Nombres invalides")
        
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="✓ Appliquer", command=apply_size,
                 bg='#10b981', fg='white', font=('Arial', 10, 'bold'),
                 padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="✗ Annuler", command=dialog.destroy,
                 bg='#6b7280', fg='white', font=('Arial', 10, 'bold'),
                 padx=20, pady=5).pack(side=tk.LEFT, padx=5)
    
    def create_default_arena(self):
        if self.WIDTH == 160 and self.HEIGHT == 144:
            self.create_gameboy_arena()
        else:
            self.create_simple_arena()
    
    def create_gameboy_arena(self):
        for y in range(80):
            for x in range(self.WIDTH):
                if (x // 8 + y // 8) % 2 < 1:
                    self.grid[y][x] = 1
        
        for y in range(115, self.HEIGHT):
            for x in range(self.WIDTH):
                self.grid[y][x] = 1
        
        for x in range(self.WIDTH):
            self.grid[112][x] = 1
            self.grid[113][x] = 1
            self.grid[114][x] = 1
        
        for y in range(100, 115):
            for x in range(10, 50):
                self.grid[y][x] = 1
        
        for x in range(10, 50):
            self.grid[99][x] = 1
        for y in range(99, 115):
            self.grid[y][10] = 1
            self.grid[y][49] = 1
        
        for y in range(40, 55):
            for x in range(110, 150):
                self.grid[y][x] = 1
        
        for x in range(110, 150):
            self.grid[39][x] = 1
            self.grid[55][x] = 1
        for y in range(39, 56):
            self.grid[y][110] = 1
            self.grid[y][149] = 1
        
        pbX1, pbY1 = 25, 107
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                if dx * dx + dy * dy <= 9:
                    self.grid[pbY1 + dy][pbX1 + dx] = 1
        self.grid[pbY1][pbX1 - 3] = 0
        self.grid[pbY1][pbX1 + 3] = 0
        
        pbX2, pbY2 = 130, 47
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                if dx * dx + dy * dy <= 9:
                    self.grid[pbY2 + dy][pbX2 + dx] = 1
        self.grid[pbY2][pbX2 - 3] = 0
        self.grid[pbY2][pbX2 + 3] = 0
    
    def create_simple_arena(self):
        ground_start = int(self.HEIGHT * 0.75)
        for y in range(ground_start, self.HEIGHT):
            for x in range(self.WIDTH):
                self.grid[y][x] = 1
        
        sep_line = ground_start - 2
        for x in range(self.WIDTH):
            if sep_line >= 0:
                self.grid[sep_line][x] = 1
        
        plat1_w = int(self.WIDTH * 0.2)
        plat1_h = int(self.HEIGHT * 0.15)
        plat1_x = int(self.WIDTH * 0.1)
        plat1_y = ground_start - plat1_h - 3
        
        if plat1_y >= 0:
            for y in range(plat1_y, min(plat1_y + plat1_h, self.HEIGHT)):
                for x in range(plat1_x, min(plat1_x + plat1_w, self.WIDTH)):
                    self.grid[y][x] = 1
        
        plat2_w = int(self.WIDTH * 0.2)
        plat2_h = int(self.HEIGHT * 0.15)
        plat2_x = int(self.WIDTH * 0.7)
        plat2_y = int(self.HEIGHT * 0.3)
        
        for y in range(plat2_y, min(plat2_y + plat2_h, self.HEIGHT)):
            for x in range(plat2_x, min(plat2_x + plat2_w, self.WIDTH)):
                self.grid[y][x] = 1
    
    def draw_canvas(self):
        self.canvas.delete('all')
        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                x1 = x * self.CELL_SIZE
                y1 = y * self.CELL_SIZE
                x2 = x1 + self.CELL_SIZE
                y2 = y1 + self.CELL_SIZE
                
                color = '#2d3748' if self.grid[y][x] == 1 else '#ffffff'
                outline = '#e2e8f0' if self.CELL_SIZE > 2 else ''
                self.canvas.create_rectangle(x1, y1, x2, y2, 
                                            fill=color, outline=outline)
        
        if self.selection_start and self.selection_end:
            x1 = min(self.selection_start[0], self.selection_end[0]) * self.CELL_SIZE
            y1 = min(self.selection_start[1], self.selection_end[1]) * self.CELL_SIZE
            x2 = (max(self.selection_start[0], self.selection_end[0]) + 1) * self.CELL_SIZE
            y2 = (max(self.selection_start[1], self.selection_end[1]) + 1) * self.CELL_SIZE
            
            self.canvas.create_rectangle(x1, y1, x2, y2, 
                                        outline='#3b82f6', width=2, dash=(5, 5))
            
            corner_size = 6
            self.canvas.create_rectangle(x1-corner_size//2, y1-corner_size//2, 
                                        x1+corner_size//2, y1+corner_size//2,
                                        fill='#3b82f6', outline='white')
            self.canvas.create_rectangle(x2-corner_size//2, y2-corner_size//2, 
                                        x2+corner_size//2, y2+corner_size//2,
                                        fill='#3b82f6', outline='white')
    
    def get_grid_coords(self, event):
        x = event.x // self.CELL_SIZE
        y = event.y // self.CELL_SIZE
        if 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT:
            return x, y
        return None, None
    
    def on_mouse_down(self, event):
        x, y = self.get_grid_coords(event)
        if x is None or y is None:
            return
        
        if self.selection_mode:
            if self.selection_start and self.selection_end:
                min_x = min(self.selection_start[0], self.selection_end[0])
                max_x = max(self.selection_start[0], self.selection_end[0])
                min_y = min(self.selection_start[1], self.selection_end[1])
                max_y = max(self.selection_start[1], self.selection_end[1])
                
                if min_x <= x <= max_x and min_y <= y <= max_y:
                    self.is_dragging_selection = True
                    self.drag_offset = (x - min_x, y - min_y)
                    
                    self.selected_region = []
                    for sy in range(min_y, max_y + 1):
                        row = []
                        for sx in range(min_x, max_x + 1):
                            row.append(self.grid[sy][sx])
                        self.selected_region.append(row)
                    
                    for sy in range(min_y, max_y + 1):
                        for sx in range(min_x, max_x + 1):
                            self.grid[sy][sx] = 0
                    
                    self.draw_canvas()
                    return
            
            self.selection_start = (x, y)
            self.selection_end = (x, y)
            self.selected_region = None
            self.draw_canvas()
        else:
            self.is_drawing = True
            self.draw_pixel(event)
    
    def on_mouse_drag(self, event):
        x, y = self.get_grid_coords(event)
        if x is None or y is None:
            return
        
        if self.selection_mode:
            if self.is_dragging_selection and self.selected_region:
                new_x = x - self.drag_offset[0]
                new_y = y - self.drag_offset[1]
                
                region_h = len(self.selected_region)
                region_w = len(self.selected_region[0]) if region_h > 0 else 0
                
                self.selection_start = (new_x, new_y)
                self.selection_end = (new_x + region_w - 1, new_y + region_h - 1)
                self.draw_canvas()
            elif self.selection_start:
                self.selection_end = (x, y)
                self.draw_canvas()
        elif self.is_drawing:
            self.draw_pixel(event)
    
    def on_mouse_up(self, event):
        if self.is_dragging_selection and self.selected_region:
            x, y = self.get_grid_coords(event)
            if x is not None and y is not None:
                new_x = x - self.drag_offset[0]
                new_y = y - self.drag_offset[1]
                
                region_h = len(self.selected_region)
                region_w = len(self.selected_region[0]) if region_h > 0 else 0
                
                for dy in range(region_h):
                    for dx in range(region_w):
                        dest_x = new_x + dx
                        dest_y = new_y + dy
                        if 0 <= dest_x < self.WIDTH and 0 <= dest_y < self.HEIGHT:
                            self.grid[dest_y][dest_x] = self.selected_region[dy][dx]
                
                self.selection_start = (new_x, new_y)
                self.selection_end = (new_x + region_w - 1, new_y + region_h - 1)
                self.mark_as_modified()
            
            self.is_dragging_selection = False
            self.draw_canvas()
        
        self.is_drawing = False
    
    def draw_pixel(self, event):
        x, y = self.get_grid_coords(event)
        if x is not None and y is not None:
            self.grid[y][x] = self.draw_mode
            self.mark_as_modified()
            self.draw_canvas()
    
    def clear_grid(self):
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment tout effacer ?"):
            self.grid = [[0 for _ in range(self.WIDTH)] for _ in range(self.HEIGHT)]
            self.mark_as_modified()
            self.draw_canvas()
    
    def save_jack_code(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".jack",
            filetypes=[("Jack files", "*.jack"), ("All files", "*.*")],
            initialfile="pokemon_arena.jack"
        )
        
        if filename:
            code = self.generate_jack_code()
            with open(filename, 'w') as f:
                f.write(code)
            messagebox.showinfo("Succès", f"Code Jack sauvegardé dans:\n{filename}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PokemonArenaEditor(root)
    root.mainloop()