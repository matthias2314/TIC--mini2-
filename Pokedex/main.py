import sys
from PyQt6 import QtWidgets, QtCore
from pokedex_ui import Ui_MainWindow as Ui_PantallaPrincipal
from pokedex import Pokedex

class PantallaPrincipal(QtWidgets.QMainWindow, Ui_PantallaPrincipal):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Pantalla Principal")

        # === Now connect all 4 buttons ===
        self.Adelante.clicked.connect(self.abrir_pokedex)
        self.Atras.clicked.connect(self.abrir_pokedex)
        self.Random.clicked.connect(self.abrir_pokedex)
        self.Menu.clicked.connect(self.abrir_pokedex)

    def keyPressEvent(self, event):
        # Press D to open Pokédex
        if event.key() == QtCore.Qt.Key.Key_D:
            self.abrir_pokedex()

    def abrir_pokedex(self):
        self.pokedex = Pokedex()
        self.pokedex.show()
        self.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ventana = PantallaPrincipal()
    ventana.show()
    sys.exit(app.exec())
