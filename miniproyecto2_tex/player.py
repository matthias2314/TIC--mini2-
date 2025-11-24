import os, json, time, random
from datetime import datetime
import paramiko

# --- Imported minigames ---
from minigames.memory_game import play_memory_game
from minigames.juego_ecuacion import run_equation_game
from minigames.juego_colores import run_reaction_game
from minigames.juego_globos import run_balloon_game

# =====================================================
# SSH CONFIG 
# =====================================================
HOST_IP = "192.168.0.24"
HOST_PORT = 22
HOST_USERNAME = "minipc"
HOST_PASSWORD = "P0ck3tM0nst3rs"

# Your required .log file
LOG_FILE = "player_events.log"

# Professor’s folder (you said you will fix later)
HOST_TARGET_FOLDER = f"/home/minipc/Desktop/Game_App/Player_logs/{LOG_FILE}"

# =====================================================
# LOCAL PATHS
# =====================================================
PLAYER_LOG = os.path.join("logs", LOG_FILE)
PLAYER_ID = "P001"

os.makedirs("logs", exist_ok=True)


# =====================================================
# SSH UPLOAD FUNCTION
# =====================================================
def upload_log_via_ssh():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST_IP, HOST_PORT, HOST_USERNAME, HOST_PASSWORD)

        sftp = ssh.open_sftp()

        # Ensure directory exists
        try:
            sftp.stat(HOST_TARGET_FOLDER)
        except:
            sftp.mkdir(HOST_TARGET_FOLDER)

        # Upload log
        remote_path = HOST_TARGET_FOLDER
        sftp.put(PLAYER_LOG, remote_path)

        sftp.close()
        ssh.close()
        print(f"[SSH] Log file uploaded → {remote_path}")

    except Exception as e:
        print(f"[SSH ERROR]: {e}")


# =====================================================
# LOGGING FUNCTION
# =====================================================
def log_player_event(stage, game_name, action, result):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "stage": stage,
        "PlayerID": PLAYER_ID,
        "GameName": game_name,
        "Action": action,
        "Result": result
    }

    with open(PLAYER_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    upload_log_via_ssh()


# =====================================================
# WAIT FOR HOST ACCEPTANCE (game_status.log)
# =====================================================
def wait_for_host_accept():
    STATUS_FILE = "/home/minipc/Desktop/miniproyecto2/game_status.log"

    print("Waiting for host… (looking for Action: Accepted)")

    last_line = None

    while True:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(HOST_IP, HOST_PORT, HOST_USERNAME, HOST_PASSWORD)

            sftp = ssh.open_sftp()

            try:
                remote_file = sftp.open(STATUS_FILE, "r")
                lines = remote_file.readlines()

                if lines:
                    new_line = lines[-1].strip()

                    if new_line != last_line:
                        last_line = new_line
                        print(f"[HOST MESSAGE] {new_line}")

                        try:
                            data = json.loads(new_line)
                        except:
                            print("Invalid JSON, skipping")
                            continue

                        if data.get("Action") == "Accepted":
                            print("Host accepted. Beginning rounds!")
                            remote_file.close()
                            sftp.close()
                            ssh.close()
                            return  # DONE — return control to play_game()

                remote_file.close()

            except IOError:
                pass  # File not created yet

            sftp.close()
            ssh.close()

        except Exception as e:
            print(f"Error while reading host file: {e}")

        time.sleep(1)


# =====================================================
# MAIN GAME LOOP (3 ROUNDS)
# =====================================================
def play_game():
    wait_for_host_accept()

    ROUNDS = 3

    for round_num in range(1, ROUNDS + 1):
        print(f"\n===== ROUND {round_num}/3 =====")

        # Random game selection
        game = random.choice([
            "MemoryGame",
            "EquationGame",
            "ReactionGame",
            "BalloonGame"
        ])

        log_player_event(f"Round{round_num}", game, "Start", "Running")
        print(f"Starting game → {game}")

        # Run selected game
        if game == "MemoryGame":
            result = play_memory_game()

        elif game == "EquationGame":
            score = run_equation_game()
            result = "Win" if score > 0 else "Lose"

        elif game == "ReactionGame":
            win = run_reaction_game()
            result = "Win" if win else "Lose"

        elif game == "BalloonGame":
            win = run_balloon_game()
            result = "Win" if win else "Lose"

        else:
            result = "Lose"

        log_player_event(f"Round{round_num}", game, "End", result)
        print(f"[RESULT] {game} finished → {result}")

        time.sleep(1)

    print("\nAll 3 rounds completed!")


# =====================================================
# RUN PROGRAM
# =====================================================
if __name__ == "__main__":
    play_game()
