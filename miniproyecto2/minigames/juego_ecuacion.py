import sys
import random
import time
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout
)
from PyQt6.QtCore import Qt, QTimer


class EquationGame(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Equation Solver Game")
        self.setGeometry(400, 300, 400, 250)

        # --- UI Elements ---
        layout = QVBoxLayout()

        self.info_label = QLabel("Solve the equation for x:")
        self.info_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(self.info_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.equation_label = QLabel("")
        self.equation_label.setStyleSheet("font-size: 20px; font-weight: bold; color: blue;")
        layout.addWidget(self.equation_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Enter your answer")
        self.answer_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.answer_input)

        self.submit_button = QPushButton("Submit")
        self.submit_button.setStyleSheet("font-size: 14px; padding: 5px;")
        self.submit_button.clicked.connect(self.check_answer)
        layout.addWidget(self.submit_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.result_label = QLabel("")
        self.result_label.setStyleSheet("font-size: 16px; color: green;")
        layout.addWidget(self.result_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.timer_label = QLabel("Time: 15s")
        self.timer_label.setStyleSheet("font-size: 18px; color: red;")
        layout.addWidget(self.timer_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.score_label = QLabel("")
        self.score_label.setStyleSheet("font-size: 18px; color: purple;")
        layout.addWidget(self.score_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

        # --- Game Variables ---
        self.score = 100
        self.time_left = 15
        self.start_time = time.time()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

        self.finished = False  # indicates when game ends

        # --- Start game ---
        self.generate_equation()

    def generate_equation(self):
        """Generates random equation with integer solution"""
        self.solution = random.randint(-9, 9)
        a = random.choice([i for i in range(-9, 10) if i != 0])
        b = random.randint(-9, 9)
        c = a * self.solution + b

        b_str = f"+ {b}" if b >= 0 else f"- {-b}"
        self.equation_label.setText(f"{a}x {b_str} = {c}")
        self.answer_input.clear()
        self.result_label.setText("")

    def check_answer(self):
        """Check if user’s answer is correct"""
        if self.time_left <= 0 or self.finished:
            return

        try:
            user_answer = int(self.answer_input.text())
        except ValueError:
            self.result_label.setText("Please enter a valid number.")
            self.result_label.setStyleSheet("color: red; font-size: 16px;")
            return

        if user_answer == self.solution:
            elapsed = int(time.time() - self.start_time)
            if elapsed >= 6:
                self.score = max(0, 100 - (elapsed - 5) * 10)

            self.finish_game(correct=True)
        else:
            self.result_label.setText("❌ Wrong! Try again.")
            self.result_label.setStyleSheet("color: red; font-size: 16px;")

    def update_timer(self):
        self.time_left -= 1
        self.timer_label.setText(f"Time: {self.time_left}s")

        if self.time_left <= 0:
            self.finish_game(correct=False)

    def finish_game(self, correct):
        """Ends game and closes after short delay"""
        self.finished = True
        self.timer.stop()
        self.submit_button.setEnabled(False)
        self.answer_input.setEnabled(False)

        if correct:
            self.result_label.setText(f"✅ Correct! x = {self.solution}")
            self.result_label.setStyleSheet("color: green; font-size: 16px;")
        else:
            self.result_label.setText(f"⏰ Time’s up! x = {self.solution}")
            self.result_label.setStyleSheet("color: red; font-size: 16px;")
            self.score = 0

        self.equation_label.setText("Game Over!")
        self.timer_label.setText("Time: 0s")
        self.score_label.setText(f"Final Score: {self.score}")

        # Auto-close window after 2 seconds
        QTimer.singleShot(2000, self.close)


def run_equation_game():
    """Runs the game and returns final score (blocking until finished)."""
    app = QApplication(sys.argv)
    game = EquationGame()

    game.show()
    app.exec()

    return game.score


# Run standalone for testing
if __name__ == "__main__":
    final_score = run_equation_game()
    print(f"Final score: {final_score}")
