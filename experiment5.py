import pygame
import csv
import time
import random
import pickle
from config import *
from env import load_fixed_map, place_random
from utils.smart_cat_utils import smart_move_cat
from cat_agent import SmartCat, PredictiveCat, BurstMoveCat
from agent import (
    RandomMouse, RunAwayMouse, SmartRunAwayMouse,
    PredictiveMouse, CornerMouse, MemoryMouse
)
from agent_qlearning import QLearningMouse



#  Load the trained Q-table
with open("q_table.pkl", "rb") as f:
    q_table = pickle.load(f)

ESCAPE_THRESHOLD = 200
REPEATS = 50
map_names = ["easy", "hard"]

cat_classes = {
    "SmartCat": SmartCat,
    "PredictiveCat": PredictiveCat,
    "BurstMoveCat": BurstMoveCat
}

mouse_classes = [
    RandomMouse, RunAwayMouse, CornerMouse,
    MemoryMouse, SmartRunAwayMouse, PredictiveMouse
]

def run_trial(trial_id, map_name, cat_name, repeat):
    pygame.init()
    screen = pygame.display.set_mode((1, 1))
    clock = pygame.time.Clock()

    grid = load_fixed_map(map_name)
    grid_size = len(grid)
    cat = cat_classes[cat_name]()
    cat_pos = place_random(grid)

    used = {cat_pos}
    mice = []

    # Add six standard mice (no skills)
    for MouseCls in mouse_classes:
        while True:
            pos = place_random(grid)
            if pos not in used:
                used.add(pos)
                break
        m = MouseCls(pos[0], pos[1], pygame.Surface((CELL_SIZE, CELL_SIZE)), skills=[])
        mice.append(m)

    # Add one Predictive mouse with teleport skill
    while True:
        pos = place_random(grid)
        if pos not in used:
            used.add(pos)
            break
    smart = PredictiveMouse(pos[0], pos[1], pygame.Surface((CELL_SIZE, CELL_SIZE)), skills=["teleport"])
    mice.append(smart)

    # Add one Q-learning mouse (no skill)
    while True:
        pos = place_random(grid)
        if pos not in used:
            used.add(pos)
            break
    qmouse = QLearningMouse(pos[0], pos[1], pygame.Surface((CELL_SIZE, CELL_SIZE)), q_table)
    qmouse.training = False
    mice.append(qmouse)

    results = []
    step = 0

    while mice and step < ESCAPE_THRESHOLD:
        cat_pos = cat.move(cat_pos, mice, grid, grid_size)
        remaining = []

        for m in mice:
            if m.age >= ESCAPE_THRESHOLD:
                results.append({
                    "trial": trial_id,
                    "repeat": repeat,
                    "map": map_name,
                    "cat_strategy": cat.name,
                    "mouse_strategy": m.strategy,
                    "skills": ",".join(m.skills) if hasattr(m, "skills") else "none",
                    "caught": 0,
                    "steps": m.age
                })
                continue

            pos = getattr(m, "position", (m.x, m.y))
            if pos == cat_pos:
                results.append({
                    "trial": trial_id,
                    "repeat": repeat,
                    "map": map_name,
                    "cat_strategy": cat.name,
                    "mouse_strategy": m.strategy,
                    "skills": ",".join(m.skills) if hasattr(m, "skills") else "none",
                    "caught": 1,
                    "steps": m.age
                })
                continue

            m.move(grid, grid_size, cat_pos)
            new_pos = getattr(m, "position", (m.x, m.y))
            if new_pos == cat_pos:
                results.append({
                    "trial": trial_id,
                    "repeat": repeat,
                    "map": map_name,
                    "cat_strategy": cat.name,
                    "mouse_strategy": m.strategy,
                    "skills": ",".join(m.skills) if hasattr(m, "skills") else "none",
                    "caught": 1,
                    "steps": m.age
                })
            else:
                remaining.append(m)

        mice = remaining
        step += 1
        clock.tick(FPS)

    # Append surviving mice and their outcome
    for m in mice:
        results.append({
            "trial": trial_id,
            "repeat": repeat,
            "map": map_name,
            "cat_strategy": cat.name,
            "mouse_strategy": m.strategy,
            "skills": ",".join(m.skills) if hasattr(m, "skills") else "none",
            "caught": 0 if m.age >= ESCAPE_THRESHOLD else 1,
            "steps": m.age
        })

    pygame.quit()
    return results

def run_experiment5():
    all_results = []
    trial_id = 1
    total = len(map_names) * len(cat_classes) * REPEATS

    start_time = time.time()
    for map_name in map_names:
        for cat_name in cat_classes:
            for repeat in range(1, REPEATS + 1):
                print(f"🎯 Trial {trial_id}/{total} | Map={map_name}, Cat={cat_name}, Repeat={repeat}")
                trial_data = run_trial(trial_id, map_name, cat_name, repeat)
                all_results.extend(trial_data)
                trial_id += 1

                elapsed = time.time() - start_time
                eta = elapsed / trial_id * (total - trial_id)
                print(f"⏱️ Time: {elapsed:.1f}s | ETA: {eta/60:.1f} min")

    filename = f"experiment5_results_{time.strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
        writer.writeheader()
        writer.writerows(all_results)

    print(f"✅ Results saved to {filename}")

if __name__ == "__main__":
    run_experiment5()

