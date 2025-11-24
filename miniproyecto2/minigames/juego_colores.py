# minigames/reaction_game.py
import sys
import random
import time

from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import QTimer, Qt

# -------------------------------------------------------------
# Optional GPIO Support (Raspberry Pi Only)
# -------------------------------------------------------------
USE_GPIO = False
try:
    from gpiozero import Button
    button_black = Button(27)
    button_blue  = Button(18)
    button_red   = Button(17)
    USE_GPIO = True
except Exception:
    # GPIO not available → fallback to keyboard input
    button_black = None
    button_blue = None
    button_red = None


# -------------------------------------------------------------
# Reaction Game Class
# -------------------------------------------------------------
class ReactionGame(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Reaction Game")
        self.setGeometry(200, 200, 400, 200)

        # Game state
        self.colors = ["Black", "Blue", "Red"]
        self.current_color = None
        self.reaction_times = []
        self.scores = []
        self.max_clicks = 3
        self.clicks_done = 0
        self.start_time = 0

        # GUI
        self.layout = QVBoxLayout()

        self.label = QLabel("Press the correct button!")
        self.label.setStyleSheet("font-size: 16px;")
        self.layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.result_label = QLabel("")
        self.result_label.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.result_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.score_label = QLabel("Score: 0")
        self.score_label.setStyleSheet("font-size: 14px; color: green;")
        self.layout.addWidget(self.score_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self.layout)

        # Bind GPIO or keyboard
        self.setup_input()

        # Start game after 1 second
        QTimer.singleShot(1000, self.show_button)

    # ---------------------------------------------------------
    # Input Handling (GPIO or keyboard)
    # ---------------------------------------------------------
    def setup_input(self):
        if USE_GPIO:
            button_black.when_pressed = lambda: self.button_pressed("Black")
            button_blue.when_pressed  = lambda: self.button_pressed("Blue")
            button_red.when_pressed   = lambda: self.button_pressed("Red")
        else:
            self.label.setText("Press 1=Black, 2=Blue, 3=Red when requested.")

    def keyPressEvent(self, event):
        if USE_GPIO:
            return  # ignore keyboard on Pi

        if event.key() == Qt.Key.Key_1:
            self.button_pressed("Black")
        elif event.key() == Qt.Key.Key_2:
            self.button_pressed("Blue")
        elif event.key() == Qt.Key.Key_3:
            self.button_pressed("Red")

    # ---------------------------------------------------------
    # Game Logic
    # ---------------------------------------------------------
    def show_button(self):
        if self.clicks_done >= self.max_clicks:
            return

        self.current_color = random.choice(self.colors)
        self.label.setText(f"Press: {self.current_color}")

        self.start_time = time.time()

    def button_pressed(self, color):
        if self.clicks_done >= self.max_clicks:
            return

        reaction_time = time.time() - self.start_time

        # Scoring Logic (same as original)
        base_score = 34 if self.clicks_done == 2 else 33
        if color == self.current_color:
            if reaction_time <= 0.5:
                score = base_score
            else:
                penalty = int((reaction_time - 0.5) / 0.1)
                score = max(0, base_score - penalty * 3)
        else:
            score = 0

        self.scores.append(score)
        self.reaction_times.append((color, reaction_time))

        self.score_label.setText(f"Score: {sum(self.scores)}")

        self.clicks_done += 1

        if self.clicks_done < self.max_clicks:
            wait_time = random.uniform(2, 5) * 1000
            QTimer.singleShot(int(wait_time), self.show_button)
        else:
            self.finish_game()

    # ---------------------------------------------------------
    # End of Game
    # ---------------------------------------------------------
    def finish_game(self):
        results = "\n".join(
            [f"{i+1}. {color}: {t:.3f}s ; {s} pts"
             for i, ((color, t), s) in enumerate(zip(self.reaction_times, self.scores))]
        )
        total_score = sum(self.scores)
        self.result_label.setText(f"{results}\n\nTotal Score: {total_score}/100")

        self.label.setText("Game Finished!")
        self.score = total_score  # stored so run_reaction_game() can retrieve it


# -------------------------------------------------------------
# Public Function Called By Player Script
# -------------------------------------------------------------
def run_reaction_game():
    """
    Launches the Reaction Game GUI and waits for completion.
    Returns a dict with the result and the score.
    """

    app = QApplication(sys.argv)
    window = ReactionGame()
    window.show()
    app.exec()  # This blocks until window is closed

    return {
        "Result": "Win",
        "Score": window.score
    }

# run standalone for testing
if __name__ == "__main__":
    run_reaction_game()