
import pygame
import time
import csv
import random
import pickle
from env import load_fixed_map, place_random
from cat_agent import SmartCat, PredictiveCat, BurstMoveCat
from agent_qlearning import QLearningMouse

def run_single_game(cat_class, map_name, q_table, ESCAPE_THRESHOLD=200):
    pygame.init()
    screen = pygame.display.set_mode((1, 1))
    clock = pygame.time.Clock()

    grid = load_fixed_map(map_name)
    grid_size = len(grid)
    cat = cat_class()
    cat_pos = place_random(grid)

    mouse = QLearningMouse(*place_random(grid), None, q_table)
    mouse.training = False
    mouse.strategy = "QLearning"

    results = []
    step = 0
    start_time = time.time()

    while step < ESCAPE_THRESHOLD:
        cat_pos = cat.move(cat_pos, [mouse], grid, grid_size)
        mouse.move(grid, grid_size, cat_pos)
        if mouse.position == cat_pos:
            t_now = time.time()
            results.append({
                'cat_strategy': cat.name,
                'mouse_strategy': mouse.strategy,
                'skill': 'none',
                'caught': 1,
                'caught_time': step,
                'caught_seconds': round(t_now - start_time, 2),
                'steps': step,
                'map': map_name
            })
            break
        step += 1
        clock.tick(10000)

    if step >= ESCAPE_THRESHOLD:
        results.append({
            'cat_strategy': cat.name,
            'mouse_strategy': mouse.strategy,
            'skill': 'none',
            'caught': 0,
            'caught_time': -1,
            'caught_seconds': -1,
            'steps': step,
            'map': map_name
        })

    pygame.quit()
    return results

def run_experiment3(trials_per_combo=50, export=True):
    cat_classes = [SmartCat, PredictiveCat, BurstMoveCat]
    map_names = ["easy", "hard"]

    with open("q_table.pkl", "rb") as f:
        q_table = pickle.load(f)

    all_results = []
    total = len(cat_classes) * len(map_names) * trials_per_combo
    counter = 0
    start_global = time.time()

    for map_name in map_names:
        for cat_cls in cat_classes:
            for t in range(trials_per_combo):
                start = time.time()
                results = run_single_game(cat_cls, map_name, q_table)
                all_results.extend(results)
                counter += 1
                elapsed = time.time() - start
                avg = (time.time() - start_global) / counter
                eta = avg * (total - counter)
                print(f"[{counter}/{total}] Cat={cat_cls.__name__}, Map={map_name}, Trial={t+1} | Time: {elapsed:.2f}s | ETA: {eta/60:.1f} min")

    if export:
        filename = f"experiment3_results_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
            writer.writeheader()
            writer.writerows(all_results)
        print(f"✅ Results saved to {filename}")
    return all_results

if __name__ == "__main__":
    run_experiment3()
