import os, json, random, time
from datetime import datetime

HOST_FOLDER = "host_folder"
LOG_FILE = os.path.join("logs", "game_status.log")
MINIGAMES = ["MemoryGame", "ReactionGame", "MathGame", "LogicGame"]

os.makedirs(HOST_FOLDER, exist_ok=True)
os.makedirs("logs", exist_ok=True)

# ---------- Logging ----------
def log_host_event(stage, player_id, action, game_name=None, game_id=None, extra=None):
    event = {
        "timestamp": datetime.now().isoformat(),
        "stage": stage,
        "PlayerID": player_id,
        "Action": action,
        "GameName": game_name,
        "GameID": game_id,
    }
    if extra:
        event.update(extra)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

# ---------- ACK connection ----------
def wait_for_join(player_id):
    join_path = os.path.join(HOST_FOLDER, f"join_{player_id}.json")
    print("🖥️ Host waiting for Join request...")
    while not os.path.exists(join_path):
        time.sleep(1)
    with open(join_path, "r", encoding="utf-8") as f:
        join_data = json.load(f)
    os.remove(join_path)

    print(f"✅ Player {player_id} connected (Join received)")
    log_host_event("Lobby", player_id, "Accepted")

    # Send ACK
    ack_data = {"Action": "Accepted", "PlayerID": player_id, "timestamp": datetime.now().isoformat()}
    ack_path = os.path.join(HOST_FOLDER, f"ack_{player_id}.json")
    with open(ack_path, "w", encoding="utf-8") as f:
        json.dump(ack_data, f, ensure_ascii=False, indent=4)

# ---------- Game management ----------
def assign_minigame(stage, player_id):
    game = random.choice(MINIGAMES)
    game_id = f"{player_id}_{int(time.time())}"
    assignment = {
        "PlayerID": player_id,
        "stage": stage,
        "GameName": game,
        "GameID": game_id,
        "Action": "Assign",
        "timestamp": datetime.now().isoformat()
    }

    assign_path = os.path.join(HOST_FOLDER, f"assign_{player_id}.json")
    with open(assign_path, "w", encoding="utf-8") as f:
        json.dump(assignment, f, ensure_ascii=False, indent=4)

    log_host_event(stage, player_id, "Assign", game, game_id)
    print(f"🎮 Assigned {game} to {player_id} ({stage})")

def wait_for_result(player_id):
    result_path = os.path.join(HOST_FOLDER, f"result_{player_id}.json")
    while not os.path.exists(result_path):
        time.sleep(1)
    with open(result_path, "r", encoding="utf-8") as f:
        result_data = json.load(f)
    os.remove(result_path)

    log_host_event(result_data["stage"], player_id, "ResultReceived",
                   result_data["GameName"], result_data["GameID"])
    print(f"📥 Received result from {player_id}: {result_data['GameName']} -> {result_data['Result']}")
    return result_data["stage"]

# ---------- Sabotage ----------
def maybe_apply_sabotage(stage, player_id):
    if random.random() < 0.4:  # 40% chance
        effect = random.choice(["ReduceTime", "InvertControls", "RandomFail"])
        value = random.randint(1, 3)
        sabotage = {
            "timestamp": datetime.now().isoformat(),
            "stage": stage,
            "PlayerID": player_id,
            "Action": "Sabotage",
            "Effect": effect,
            "Value": value
        }
        sabotage_path = os.path.join(HOST_FOLDER, f"sabotage_{player_id}.json")
        with open(sabotage_path, "w", encoding="utf-8") as f:
            json.dump(sabotage, f, ensure_ascii=False, indent=4)
        log_host_event(stage, player_id, "Sabotage", extra={"Effect": effect, "Value": value})
        print(f"⚠️ Sabotage applied to {player_id}: {effect} ({value})")

# ---------- Main cycle ----------
def host_game_cycle(player_id):
    wait_for_join(player_id)
    print("🖥️ Host: entering Lobby...")
    log_host_event("Lobby", player_id, "Start")
    time.sleep(2)

    for round_name in ["R1", "R2"]:
        print(f"🚀 Starting {round_name}...")
        log_host_event(round_name, player_id, "Start")

        for _ in range(3):
            assign_minigame(round_name, player_id)
            stage = wait_for_result(player_id)
            maybe_apply_sabotage(stage, player_id)

        print(f"✅ {round_name} finished.")
        log_host_event(round_name, player_id, "End")

    print("🏁 Game completed!")
    log_host_event("Game", player_id, "End")

if __name__ == "__main__":
    host_game_cycle("P001")
