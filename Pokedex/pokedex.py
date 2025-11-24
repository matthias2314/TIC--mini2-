import sys
import os
import random
from PyQt6 import QtWidgets, QtGui, QtCore
from pokedex_ui import Ui_MainWindow

class Pokedex(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.Description.setWordWrap(True)
        self.Description.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # === Datos de los Pokémon ===
        self.pokemons = [
            {
                "nombre": "Charmander",
                "tipo": "Fuego",
                "descripcion": "Prefiere los lugares calientes. Cuando llueve, se dice que el vapor sale de la punta de su cola.",
                "imagen": "Img/pkm/Charmander.jpg"
            },
            {
                "nombre": "Dragonair",
                "tipo": "Dragón",
                "descripcion": "Se dice que tiene una energía mística que le permite controlar el clima.",
                "imagen": "Img/pkm/dragonair.jpg"
            },
            {
                "nombre": "Gengar",
                "tipo": "Fantasma/Veneno",
                "descripcion": "A menudo se esconde en las sombras de las personas para asustarlas.",
                "imagen": "Img/pkm/Gengar.jpg"
            },
            {
                "nombre": "Lapras",
                "tipo": "Agua/Hielo",
                "descripcion": "Un Pokémon amable que transporta personas sobre su espalda a través del mar.",
                "imagen": "Img/pkm/Lapras.jpg"
            },
            {
                "nombre": "Lucario",
                "tipo": "Lucha/Acero",
                "descripcion": "Puede percibir las emociones y pensamientos de los demás gracias a su aura.",
                "imagen": "Img/pkm/lucario.jpg"
            },
            {
                "nombre": "mew",
                "tipo": "Psíquico",
                "descripcion": "Se dice que posee el ADN de todos los Pokémon. Puede hacerse invisible a voluntad.",
                "imagen": "Img/pkm/mew.jpg"
            },
            {
                "nombre": "pikachu",
                "tipo": "Eléctrico",
                "descripcion": "Cuando se enoja, libera una poderosa descarga eléctrica.",
                "imagen": "Img/pkm/pikachu.jpg"
            },
            {
                "nombre": "piplup",
                "tipo": "Agua",
                "descripcion": "Un Pokémon orgulloso que odia aceptar ayuda. Nada muy rápido pese a su tamaño.",
                "imagen": "Img/pkm/piplup.jpg"
            },
            {
                "nombre": "Snorlax",
                "tipo": "Normal",
                "descripcion": "Duerme casi todo el día. Solo se despierta para comer enormes cantidades de comida.",
                "imagen": "Img/pkm/snorlax.jpg"
            },
            {
                "nombre": "Squirtle",
                "tipo": "Agua",
                "descripcion": "Dispara agua a alta presión de su boca. Su caparazón lo protege de los ataques.",
                "imagen": "Img/pkm/squirtle.jpg"
            },
        ]

        self.index = 0
        self.actualizar_pokemon()

        # === Conectar botones ===
        self.Adelante.clicked.connect(self.pokemon_siguiente)
        self.Atras.clicked.connect(self.pokemon_anterior)
        self.Random.clicked.connect(self.pokemon_aleatorio)
        self.Menu.clicked.connect(self.retour_menu)  # <-- ajouté ici pour le bouton “Menu”

    # === Actualizar la interfaz con los datos del Pokémon ===
    def actualizar_pokemon(self):
        p = self.pokemons[self.index]

        self.NombreP.setText(f"<p align='center'><span style='font-size:12pt; font-weight:600;'>{p['nombre']}</span></p>")
        self.Tipo.setText(f"<p align='center'><span style='font-size:12pt; font-weight:600;'>{p['tipo']}</span></p>")
        self.Description.setText(f"<p align='center'><span style='font-size:11pt; font-weight:600;'>{p['descripcion']}</span></p>")

        if os.path.exists(p["imagen"]):
            self.PokemonIm.setPixmap(QtGui.QPixmap(p["imagen"]))
        else:
            self.PokemonIm.setPixmap(QtGui.QPixmap())

        self.cambiar_color_led(p["tipo"])

    def cambiar_color_led(self, tipo):
        tipo = tipo.lower()
        color = "gray"
        if "fuego" in tipo:
            color = "red"
        elif "agua" in tipo:
            color = "blue"
        elif "eléctrico" in tipo:
            color = "yellow"
        elif "planta" in tipo:
            color = "green"
        elif "psíquico" in tipo:
            color = "purple"
        elif "normal" in tipo:
            color = "lightgray"
        elif "hielo" in tipo:
            color = "cyan"
        elif "dragón" in tipo:
            color = "orange"
        elif "lucha" in tipo:
            color = "brown"
        elif "fantasma" in tipo:
            color = "indigo"
        elif "veneno" in tipo:
            color = "violet"
        elif "acero" in tipo:
            color = "silver"

        self.LED.setStyleSheet(
            f"background-color: {color}; border-radius: 30px; border: 2px solid black;"
        )

    def pokemon_siguiente(self):
        self.index = (self.index + 1) % len(self.pokemons)
        self.actualizar_pokemon()

    def pokemon_anterior(self):
        self.index = (self.index - 1) % len(self.pokemons)
        self.actualizar_pokemon()

    def pokemon_aleatorio(self):
        self.index = random.randint(0, len(self.pokemons) - 1)
        self.actualizar_pokemon()

    # === Contrôle clavier ===
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_D:
            self.pokemon_siguiente()
        elif event.key() == QtCore.Qt.Key.Key_S:
            self.retour_menu()

    # === Retourner au menu principal ===
    def retour_menu(self):
        from main import PantallaPrincipal  # import local pour éviter boucle d'import
        self.menu = PantallaPrincipal()
        self.menu.show()
        self.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ventana = Pokedex()
    ventana.show()
    sys.exit(app.exec())
