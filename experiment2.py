
import pygame
import time
import csv
import random
from config import *
from env import load_fixed_map, place_random
from cat_agent import SmartCat, PredictiveCat, BurstMoveCat
from agent import PredictiveMouse

# config
ESCAPE_THRESHOLD = 200
NUM_TRIALS = 50
SKILLS = ["dash", "shield", "teleport", "smoke", None]
MAPS = ["easy", "hard"]
CATS = [SmartCat, PredictiveCat, BurstMoveCat]

def run_single_game(cat_cls, skill, map_name):
    pygame.init()
    screen = pygame.display.set_mode((1, 1))
    clock = pygame.time.Clock()

    grid = load_fixed_map(map_name)
    grid_size = len(grid)
    cat = cat_cls()
    cat_pos = place_random(grid)

    mouse_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
    skills = [skill] if skill else []
    x, y = place_random(grid)
    mouse = PredictiveMouse(x, y, mouse_img, skills=skills)
    mice = [mouse]

    step = 0
    results = []
    start_time = time.time()

    while mice and step < ESCAPE_THRESHOLD:
        cat_pos = cat.move(cat_pos, mice, grid, grid_size)
        remaining = []

        for m in mice:
            m.age += 1
            if m.age >= ESCAPE_THRESHOLD:
                results.append({
                    'cat_strategy': cat.name,
                    'mouse_strategy': m.strategy,
                    'skill': skill if skill else "none",
                    'caught': 0,
                    'caught_time': -1,
                    'caught_seconds': -1,
                    'steps': m.age,
                    'map': map_name
                })
                continue
            if (m.x, m.y) == cat_pos:
                t_now = time.time()
                results.append({
                    'cat_strategy': cat.name,
                    'mouse_strategy': m.strategy,
                    'skill': skill if skill else "none",
                    'caught': 1,
                    'caught_time': step,
                    'caught_seconds': round(t_now - start_time, 2),
                    'steps': step,
                    'map': map_name
                })
                continue
            m.move(grid, grid_size, cat_pos)
            if (m.x, m.y) == cat_pos:
                t_now = time.time()
                results.append({
                    'cat_strategy': cat.name,
                    'mouse_strategy': m.strategy,
                    'skill': skill if skill else "none",
                    'caught': 1,
                    'caught_time': step,
                    'caught_seconds': round(t_now - start_time, 2),
                    'steps': step,
                    'map': map_name
                })
            else:
                remaining.append(m)

        mice = remaining
        step += 1
        clock.tick(FPS)

    for m in mice:
        results.append({
            'cat_strategy': cat.name,
            'mouse_strategy': m.strategy,
            'skill': skill if skill else "none",
            'caught': 0,
            'caught_time': -1,
            'caught_seconds': -1,
            'steps': step,
            'map': map_name
        })

    pygame.quit()
    return results


def run_experiment_two(export_csv=True):
    all_results = []
    total_trials = len(CATS) * len(MAPS) * len(SKILLS) * NUM_TRIALS
    trial_count = 0
    start_all = time.time()

    for cat_cls in CATS:
        for map_name in MAPS:
            for skill in SKILLS:
                for trial in range(NUM_TRIALS):
                    print(f"▶️ Trial {trial+1}/{NUM_TRIALS} | Cat={cat_cls.__name__} Map={map_name} Skill={skill}")
                    start = time.time()
                    results = run_single_game(cat_cls, skill, map_name)
                    all_results.extend(results)

                    # 进度与时间
                    trial_count += 1
                    duration = time.time() - start
                    avg = (time.time() - start_all) / trial_count
                    eta = avg * (total_trials - trial_count)
                    print(f"⏱️ Trial done in {duration:.2f}s | ETA: {eta / 60:.1f} min\n")

    if export_csv:
        filename = f"experiment2_results_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                'cat_strategy', 'mouse_strategy', 'skill',
                'caught', 'caught_time', 'caught_seconds',
                'steps', 'map'
            ])
            writer.writeheader()
            writer.writerows(all_results)
        print(f"✅ Results saved to {filename}")

    return all_results


if __name__ == "__main__":
    run_experiment_two()
