#!/usr/bin/env python3
import sys
import random
from PyQt6.QtCore import Qt, QTimer, QRect
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QApplication, QWidget
from gpiozero import Button

# ---------------- Hardware ----------------
button = Button(17)

# ---------------- Constantes ----------------
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
CURSOR_SIZE = 40
GAME_DURATION = 10000  # ms
BALLOON_SPAWN_START = 800
BALLOON_SPAWN_MIN = 250

# ---------------- Balloon ----------------
class Balloon:
    def __init__(self, x, color):
        self.x = x
        self.y = -40
        self.size = 40
        self.color = color
        self.speed = random.randint(3,6)
    def move(self):
        self.y += self.speed
    def rect(self):
        return QRect(int(self.x), int(self.y), self.size, self.size)

# ---------------- Juego ----------------
class BalloonGame(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Balloon Game")
        self.setFixedSize(SCREEN_WIDTH, SCREEN_HEIGHT)

        self.cursor_x = SCREEN_WIDTH/2 - CURSOR_SIZE/2
        self.cursor_y = SCREEN_HEIGHT/2 - CURSOR_SIZE/2
        self.balloons = []
        self.spawn_interval = BALLOON_SPAWN_START
        self.running = True
        self.result_value = None

        # Timer de actualización
        self.timer_update = QTimer()
        self.timer_update.timeout.connect(self.update_game)
        self.timer_update.start(16)  # 60 FPS

        # Timer de spawn de globos
        self.timer_spawn = QTimer()
        self.timer_spawn.timeout.connect(self.spawn_balloon)
        self.timer_spawn.start(self.spawn_interval)

        # Timer de fin de juego
        self.timer_game = QTimer()
        self.timer_game.setSingleShot(True)
        self.timer_game.timeout.connect(self.game_over)
        self.timer_game.start(GAME_DURATION)

    def update_game(self):
        if not self.running:
            return
        for b in self.balloons:
            b.move()
        if button.is_pressed:
            self.check_collisions()
        for b in self.balloons:
            if b.y > SCREEN_HEIGHT:
                self.running = False
                self.result_value = "Lose"
                self.update()
                return
        self.update()

    def check_collisions(self):
        cursor_rect = QRect(int(self.cursor_x), int(self.cursor_y), CURSOR_SIZE, CURSOR_SIZE)
        self.balloons = [b for b in self.balloons if not cursor_rect.intersects(b.rect())]

    def spawn_balloon(self):
        x = random.randint(20, SCREEN_WIDTH - 60)
        color = random.choice(["red","blue","yellow","green","magenta","cyan"])
        self.balloons.append(Balloon(x, QColor(color)))
        if self.spawn_interval > BALLOON_SPAWN_MIN:
            self.spawn_interval -= 20
            self.timer_spawn.start(self.spawn_interval)

    def game_over(self):
        self.running = False
        self.result_value = "Win" if len(self.balloons)==0 else "Lose"
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#1e1e2e"))

        for b in self.balloons:
            painter.setBrush(b.color)
            painter.setPen(Qt.GlobalColor.black)
            painter.drawEllipse(int(b.x), int(b.y), b.size, b.size)

        painter.setBrush(QColor("white"))
        painter.drawRect(int(self.cursor_x), int(self.cursor_y), CURSOR_SIZE, CURSOR_SIZE)

        if not self.running:
            painter.setPen(QColor("white"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                             "WIN" if self.result_value=="Win" else "LOSE")

# ---------------- Main ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    game_win = BalloonGame()
    game_win.show()
    app.exec()





