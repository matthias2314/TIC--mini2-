# minigames/memory_game.py

import sys, random, string, json, time, os
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import QTimer, Qt

# ---------- Logging ----------
def log_event(player_id, game_name, event_type, result, extra_data=None):
    os.makedirs("logs", exist_ok=True)
    event = {
        "timestamp": datetime.now().isoformat(),
        "player_id": player_id,
        "game_name": game_name,
        "event_type": event_type,
        "result": result,
        "extra_data": extra_data or {}
    }
    with open(os.path.join("logs", f"{game_name.lower()}_log.json"), "a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False) + "\n")

# ---------- Memory Game ----------
class MemoryGame(QWidget):
    def __init__(self, player_id="P001"):
        super().__init__()
        self.player_id = player_id
        self.sequence = ""
        self.level = 4
        self.round = 0
        self.points = 0
        self.time_left = 15
        self.game_active = False

        self.setWindowTitle("Memory Game")
        self.setGeometry(500, 200, 400, 300)

        layout = QVBoxLayout()
        self.timer_label = QLabel(f"Time: {self.time_left}")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(self.timer_label)

        self.seq_label = QLabel("")
        self.seq_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.seq_label.setStyleSheet("font-size: 32px; font-weight: bold;")
        layout.addWidget(self.seq_label)

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Enter sequence here")
        self.input_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_box.returnPressed.connect(self.check_answer)
        layout.addWidget(self.input_box)

        self.start_button = QPushButton("Start Game")
        self.start_button.clicked.connect(self.start_game)
        layout.addWidget(self.start_button)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.check_answer)
        self.submit_button.setEnabled(False)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

        self.main_timer = QTimer()
        self.main_timer.timeout.connect(self.update_main_timer)

        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_sequence)

    def start_game(self):
        self.start_button.setEnabled(False)
        self.submit_button.setEnabled(True)
        self.game_active = True
        self.sequence = ""
        self.round = 0
        self.points = 0
        self.time_left = 15
        self.timer_label.setText(f"Time: {self.time_left}")
        self.seq_label.setText("")
        self.input_box.clear()
        self.main_timer.start(1000)
        log_event(self.player_id, "MemoryGame", "GameStart", "Started", {"initial_level": self.level})
        self.next_round()

    def generate_sequence(self):
        chars = string.ascii_uppercase + string.digits
        if self.sequence == "":
            self.sequence = ''.join(random.choice(chars) for _ in range(self.level))
        else:
            self.sequence += random.choice(chars)

    def next_round(self):
        if self.round >= 5:
            self.end_game()
            return
        self.generate_sequence()
        self.seq_label.setText(self.sequence)
        self.input_box.clear()
        self.hide_timer.start(1000)
        log_event(self.player_id, "MemoryGame", "RoundStart", "ShownSequence", {"round": self.round + 1, "sequence": self.sequence})

    def hide_sequence(self):
        self.seq_label.setText("")

    def check_answer(self):
        if not self.game_active:
            return
        user_input = self.input_box.text().strip().upper()
        correct = user_input == self.sequence
        if correct:
            self.points += 20
            self.round += 1
            log_event(self.player_id, "MemoryGame", "RoundEnd", "Correct", {"round": self.round, "points": self.points})
            if self.round >= 5:
                self.end_game()
            else:
                self.next_round()
        else:
            log_event(self.player_id, "MemoryGame", "RoundEnd", "Incorrect", {"round": self.round + 1})
            self.end_game()

    def update_main_timer(self):
        self.time_left -= 1
        self.timer_label.setText(f"Time: {self.time_left}")
        if self.time_left <= 0:
            log_event(self.player_id, "MemoryGame", "Timer", "Expired", {"points": self.points})
            self.end_game()

    def end_game(self):
        if not self.game_active:
            return
        self.main_timer.stop()
        self.submit_button.setEnabled(False)
        self.start_button.setEnabled(True)
        self.game_active = False
        log_event(self.player_id, "MemoryGame", "GameEnd", "Finished", {"final_round": self.round, "final_points": self.points})
        msg = QMessageBox()
        msg.setWindowTitle("Game Over")
        msg.setText(f"Game Over!\nRounds: {self.round}\nPoints: {self.points}/100")
        msg.exec()
        self.sequence = ""
        self.round = 0
        self.points = 0
        self.time_left = 15
        self.timer_label.setText(f"Time: {self.time_left}")
        self.seq_label.setText("")
        self.input_box.clear()
        self.submit_button.setEnabled(False)

# ---------- Game launcher ----------
def play_memory_game():
    """Function used by main player code to launch this game."""
    app = QApplication(sys.argv)
    window = MemoryGame()
    window.show()
    app.exec()
    # Return a dummy result for host
    return "Win" if window.points >= 60 else "Lose"
