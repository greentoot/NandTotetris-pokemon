# GROUPE 8 Anthony

# VMTranslator

VMTranslator est un projet complet permettant de traduire du code **Jack** et **VM** vers du code **ASM**, dans le cadre du projet Nand2Tetris.  
Il inclut :

- un traducteur **Jack → VM**
- un traducteur **VM → ASM**
- plusieurs projets Jack (jeux, tests, prototypes)

## 📁 Structure du projet

```
VMTranslator/
│
├── Jack/                    # Traducteur Jack → VM
│   ├── Reader.py
│   ├── Translator.py
│   ├── jeu/                # Projets Jack (JackPokemon)
│   └── trash/              # Ancien code / tests
│
├── VM/                      # Traducteur VM → ASM
│   ├── Generator.py
│   ├── Lexer.py
│   ├── Parser.py
│   ├── Reader.py
│   ├── Translator.py
│   └── code/               # Exemples VM et ASM générés
│
└── readme/                  
```

## 🚀 Utilisation

### 1️⃣ Traduction Jack → VM

```
cd Jack
python Translator.py jeu/JackpokemonV36
```

Les fichiers `.vm` générés apparaissent dans le même dossier que les fichiers `.jack`.

### 2️⃣ Traduction VM → ASM

```
cd ../VM
python Translator.py ../Jack/jeu/JackpokemonV36 Pokemon.asm
```

## 🔧 Pipeline complet

```
cd Jack
python Translator.py jeu/MonJeu

cd ../VM
python Translator.py ../Jack/jeu/MonJeu Monjeu.asm
```


# Le jeux

```
Comment jouer aux jeux:

flèche directionnelle pour se déplacer
Entrée pour valider + interaction pnj 
ESPACE pour certaine interaction (comme pousser des rocher)
i pour ouvrir l inventaire
p pour ouvrir le pokédex
q pour quitter le jeu (ou la fenetre en cour utilisation)
t pour accéder a la team 
Dasn team on peut changer la position de certain personnage avec s et les mettre en actif avec a
```
[🎬 Télécharger / Voir la demo pokémon](poke.mp4)
[🎬 Télécharger / Voir la demo devinette](devinette.mp4)

