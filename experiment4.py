import pygame
import csv
import time
import random
import pickle
from config import *
from env import load_fixed_map, place_random
from utils.smart_cat_utils import smart_move_cat
from cat_agent import SmartCat, PredictiveCat, BurstMoveCat
from agent import PredictiveMouse
from agent_qlearning import QLearningMouse

# Load pre-trained Q-table
with open("q_table.pkl", "rb") as f:
    q_table = pickle.load(f)

ESCAPE_THRESHOLD = 200
REPEATS = 10
map_names = ["easy", "hard"]
skills_pool = ["dash", "shield", "teleport", "smoke"]
cat_classes = {
    "SmartCat": SmartCat,
    "PredictiveCat": PredictiveCat,
    "BurstMoveCat": BurstMoveCat
}

def create_mouse(strategy, x, y, img, skills=None):
    if strategy == "QLearning":
        m = QLearningMouse(x, y, img, q_table)
        m.training = False
        return m
    elif strategy == "Predictive":
        return PredictiveMouse(x, y, img, skills=skills or [])
    else:
        raise ValueError("Unsupported strategy")

def run_trial(trial_id, map_name, cat_name, skill, repeat):
    pygame.init()
    screen = pygame.display.set_mode((1, 1))
    clock = pygame.time.Clock()

    grid = load_fixed_map(map_name)
    grid_size = len(grid)
    cat = cat_classes[cat_name]()
    cat_pos = place_random(grid)

    # Create 3 mice: Q-learning, Predictive (no skill), Predictive + skill
    mice_config = [
        {"strategy": "QLearning", "skills": []},
        {"strategy": "Predictive", "skills": []},
        {"strategy": "Predictive", "skills": [skill]}
    ]

    used = {cat_pos}
    mice = []
    for conf in mice_config:
        while True:
            pos = place_random(grid)
            if pos not in used:
                used.add(pos)
                break
        m = create_mouse(conf["strategy"], pos[0], pos[1], pygame.Surface((CELL_SIZE, CELL_SIZE)), skills=conf["skills"])
        mice.append(m)

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

    # Append mice that survived till the end
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

def run_experiment4():
    all_results = []
    trial_id = 1
    total = len(map_names) * len(cat_classes) * len(skills_pool) * REPEATS
    start_time = time.time()

    for map_name in map_names:
        for cat_name in cat_classes:
            for skill in skills_pool:
                for repeat in range(1, REPEATS + 1):
                    print(f"🎯 Trial {trial_id}/{total}: map={map_name}, cat={cat_name}, skill={skill}, repeat={repeat}")
                    trial_data = run_trial(trial_id, map_name, cat_name, skill, repeat)
                    all_results.extend(trial_data)
                    trial_id += 1

                    elapsed = time.time() - start_time
                    avg_time = elapsed / trial_id
                    eta = avg_time * (total - trial_id)
                    print(f"⏱️ Trial time: {elapsed:.2f}s | ETA: {eta/60:.1f} min\n")

    filename = f"experiment4_results_{time.strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
        writer.writeheader()
        writer.writerows(all_results)

    print(f"✅ Results saved to {filename}")

if __name__ == "__main__":
    run_experiment4()
