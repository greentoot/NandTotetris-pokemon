import Parser

class Generator:
    def __init__(self, file):
        self.vm_lines = []
        self.label_count = 0
        self.symbols = {}         # nom -> {index, type, kind}
        self.var_index = 0
        self.arg_index = 0
        self.field_index = 0
        self.static_index = 0
        self.current_function = None
        self.class_name = None
        self.file = file

        self.parser = Parser.Parser(file)
        self.arbre = self.parser.jackclass()
        print(self.arbre)

    def new_label(self):
        lbl = f"LABEL_{self.label_count}"
        self.label_count += 1
        return lbl

    def generate(self, node=None):
        if node is None:
            node = self.arbre

        if isinstance(node, list):
            for n in node:
                self.generate(n)
            return

        t = node.get("type") if isinstance(node, dict) else None
        if not t:
            return

        # -------------------- CLASS --------------------
        if t == "class":
            self.class_name = node["name"]["name"]
            print(f"[DEBUG] Classe détectée : {self.class_name}")

            # Gérer les champs (field) et statiques
            self.symbols = {}
            self.field_index = 0
            self.static_index = 0
            for dec in node.get("classVarDec", []):
                kind = dec["kind"]  # 'field' ou 'static'
                for var in dec["names"]:
                    var_name = var["name"]
                    var_type = dec["varType"]["name"]
                    if kind == "field":
                        self.symbols[var_name] = {"index": self.field_index, "type": var_type, "kind": "field"}
                        print(f"[DEBUG] Champ ajouté : {var_name} (this {self.field_index})")
                        self.field_index += 1
                    elif kind == "static":
                        self.symbols[var_name] = {"index": self.static_index, "type": var_type, "kind": "static"}
                        print(f"[DEBUG] Statique ajouté : {var_name} (static {self.static_index})")
                        self.static_index += 1

            # Générer toutes les sous-routines
            for sub in node.get("subroutineDec", []):
                self.generate(sub)

        # -------------------- SUBROUTINE --------------------
        elif t == "subroutineDec":
            name = node["name"]["name"]
            kind = node["subKind"]  # constructor, method, function
            self.current_function = f"{self.class_name}.{name}"
            self.var_index = 0
            self.arg_index = 0
            print(f"[DEBUG] Sous-routine détectée : {self.current_function}")

            # Symboles locaux à la fonction
            local_symbols = self.symbols.copy()

            # Si c'est une méthode, argument 0 = this
            if kind == "method":
                local_symbols["this"] = {"index": 0, "type": self.class_name, "kind": "argument"}
                self.arg_index = 1
                print(f"[DEBUG] Ajout implicite de l'argument this (argument 0)")

            # Paramètres
            for i, param in enumerate(node.get("paramList", [])):
                var_name = param["name"]["name"]
                var_type = param["varType"]["name"]
                local_symbols[var_name] = {"index": i + self.arg_index, "type": var_type, "kind": "argument"}
                print(f"[DEBUG] Paramètre ajouté : {var_name} (argument {i + self.arg_index})")

            # Nombre de variables locales
            num_locals = sum(len(v["names"]) for v in node["body"].get("varDec", []))
            self.vm_lines.append(f"function {self.current_function} {num_locals}")

            # Constructeur = allocation
            if kind == "constructor":
                num_fields = self.field_index
                self.vm_lines.append(f"push constant {num_fields}")
                self.vm_lines.append("call Memory.alloc 1")
                self.vm_lines.append("pop pointer 0")

            # Méthode = initialise this
            if kind == "method":
                self.vm_lines.append("push argument 0")
                self.vm_lines.append("pop pointer 0")

            # Sauvegarder le contexte
            old_symbols = self.symbols
            old_var_index = self.var_index
            self.symbols = local_symbols
            self.var_index = 0
            
            # Traiter les déclarations de variables d'abord
            for v in node["body"].get("varDec", []):
                self.generate(v)
            
            # Puis les statements
            for s in node["body"].get("statements", []):
                self.generate(s)
                
            self.symbols = old_symbols
            self.var_index = old_var_index

        # -------------------- SUBROUTINE BODY --------------------
        elif t == "subroutineBody":
            # Géré dans subroutineDec
            pass

        # -------------------- VAR DECLARATION --------------------
        elif t == "varDec":
            var_type = node["varType"]["name"]
            for n in node.get("names", []):
                var_name = n["name"]
                self.symbols[var_name] = {"index": self.var_index, "type": var_type, "kind": "local"}
                print(f"[DEBUG] Déclaration locale : {var_name} (local {self.var_index})")
                self.var_index += 1

        # -------------------- LET --------------------
        elif t == "letStatement":
            var_name = node["var"]["name"]
            sym = self.symbols.get(var_name)
            if not sym:
                raise Exception(f"Variable non définie : {var_name}")
            
            # Gestion des tableaux
            if node.get("index") is not None:
                # Calculer l'adresse de base + index
                kind_to_segment = {
                    "local": "local",
                    "argument": "argument",
                    "field": "this",
                    "static": "static"
                }
                segment = kind_to_segment.get(sym["kind"], "local")
                self.vm_lines.append(f"push {segment} {sym['index']}")
                self.generate(node["index"])
                self.vm_lines.append("add")
                
                # Évaluer l'expression
                self.generate(node["expr"])
                
                # Stocker dans le tableau
                self.vm_lines.append("pop temp 0")
                self.vm_lines.append("pop pointer 1")
                self.vm_lines.append("push temp 0")
                self.vm_lines.append("pop that 0")
            else:
                # Affectation simple
                self.generate(node["expr"])
                kind_to_segment = {
                    "local": "local",
                    "argument": "argument",
                    "field": "this",
                    "static": "static"
                }
                segment = kind_to_segment.get(sym["kind"], "local")
                self.vm_lines.append(f"pop {segment} {sym['index']}")

        # -------------------- DO --------------------
        elif t == "doStatement":
            self.generate(node["call"])
            self.vm_lines.append("pop temp 0")

        # -------------------- RETURN --------------------
        elif t == "returnStatement":
            expr = node.get("expr")
            if expr is None:
                self.vm_lines.append("push constant 0")
            else:
                self.generate(expr)
            self.vm_lines.append("return")

        # -------------------- IF --------------------
        elif t == "ifStatement":
            else_label = self.new_label()
            end_label = self.new_label()
            self.generate(node["cond"])
            self.vm_lines.append("not")
            self.vm_lines.append(f"if-goto {else_label}")
            self.generate(node["then"])
            self.vm_lines.append(f"goto {end_label}")
            self.vm_lines.append(f"label {else_label}")
            if node.get("else"):
                self.generate(node["else"])
            self.vm_lines.append(f"label {end_label}")

        # -------------------- WHILE --------------------
        elif t == "whileStatement":
            start_label = self.new_label()
            end_label = self.new_label()
            self.vm_lines.append(f"label {start_label}")
            self.generate(node["cond"])
            self.vm_lines.append("not")
            self.vm_lines.append(f"if-goto {end_label}")
            self.generate(node["body"])
            self.vm_lines.append(f"goto {start_label}")
            self.vm_lines.append(f"label {end_label}")

        # -------------------- EXPRESSIONS --------------------
        elif t == "integerConstant":
            self.vm_lines.append(f"push constant {node['value']}")

        elif t == "stringConstant":
            s = node["value"]
            self.vm_lines.append(f"push constant {len(s)}")
            self.vm_lines.append("call String.new 1")
            for c in s:
                self.vm_lines.append(f"push constant {ord(c)}")
                self.vm_lines.append("call String.appendChar 2")

        elif t == "keywordConstant":
            kw = node["value"]
            if kw == "true":
                self.vm_lines.append("push constant 0")
                self.vm_lines.append("not")
            elif kw in ["false", "null"]:
                self.vm_lines.append("push constant 0")
            elif kw == "this":
                self.vm_lines.append("push pointer 0")

        elif t == "varName":
            name = node["name"]
            sym = self.symbols.get(name)
            if not sym:
                raise Exception(f"Variable non définie : {name}")
            kind_to_segment = {
                "local": "local",
                "argument": "argument",
                "field": "this",
                "static": "static"
            }
            segment = kind_to_segment.get(sym["kind"], "local")
            self.vm_lines.append(f"push {segment} {sym['index']}")

        elif t == "arrayAccess":
            var_name = node["var"]["name"]
            sym = self.symbols.get(var_name)
            if not sym:
                raise Exception(f"Variable non définie : {var_name}")
            kind_to_segment = {
                "local": "local",
                "argument": "argument",
                "field": "this",
                "static": "static"
            }
            segment = kind_to_segment.get(sym["kind"], "local")
            self.vm_lines.append(f"push {segment} {sym['index']}")
            self.generate(node["index"])
            self.vm_lines.append("add")
            self.vm_lines.append("pop pointer 1")
            self.vm_lines.append("push that 0")

        elif t == "unaryExpression":
            self.generate(node["term"])
            op = node["op"]
            if op == "-":
                self.vm_lines.append("neg")
            elif op == "~":
                self.vm_lines.append("not")

        elif t == "binaryExpression":
            self.generate(node["left"])
            self.generate(node["right"])
            op = node["op"]
            mapping = {
                "+": "add",
                "-": "sub",
                "*": "call Math.multiply 2",
                "/": "call Math.divide 2",
                "&": "and",
                "|": "or",
                "<": "lt",
                ">": "gt",
                "=": "eq",
            }
            self.vm_lines.append(mapping[op])

        # -------------------- SUBROUTINE CALL --------------------
        elif t == "subroutineCall":
            call_type = node["callType"]
            args = node.get("args", [])
            nArgs = len(args)
            
            if call_type == "qualified":
                caller_name = node["caller"]["name"]
                if caller_name in self.symbols:
                    # Appel de méthode sur une variable
                    sym = self.symbols[caller_name]
                    segment = {
                        "local": "local",
                        "argument": "argument",
                        "field": "this",
                        "static": "static"
                    }[sym["kind"]]
                    self.vm_lines.append(f"push {segment} {sym['index']}")
                    nArgs += 1
                    func_name = f"{sym['type']}.{node['name']['name']}"
                    for arg in args:
                        self.generate(arg)
                    self.vm_lines.append(f"call {func_name} {nArgs}")
                else:
                    # Appel de fonction ou constructeur
                    for arg in args:
                        self.generate(arg)
                    func_name = f"{caller_name}.{node['name']['name']}"
                    self.vm_lines.append(f"call {func_name} {nArgs}")
            else:
                # Appel simple (méthode de la classe courante)
                self.vm_lines.append("push pointer 0")
                nArgs += 1
                for arg in args:
                    self.generate(arg)
                func_name = f"{self.class_name}.{node['name']['name']}"
                self.vm_lines.append(f"call {func_name} {nArgs}")

    def save(self, out_file):
        with open(out_file, "w") as f:
            f.write("\n".join(self.vm_lines))