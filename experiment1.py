import pygame
import random
import time
import csv
from config import *
from env import load_fixed_map, place_random
from utils.smart_cat_utils import smart_move_cat
from cat_agent import SmartCat, PredictiveCat, BurstMoveCat
from agent import (
    RandomMouse, RunAwayMouse, SmartRunAwayMouse,
    PredictiveMouse, CornerMouse, MemoryMouse
)

map_names = ["easy", "hard"]

def run_single_game(cat_class, map_name="easy"):
    pygame.init()
    screen = pygame.display.set_mode((1, 1))
    clock = pygame.time.Clock()

    grid = load_fixed_map(map_name)
    grid_size = len(grid)
    cat = cat_class()
    cat_pos = place_random(grid)

    mouse_classes = [
        RandomMouse, RunAwayMouse, SmartRunAwayMouse,
        PredictiveMouse, CornerMouse, MemoryMouse
    ]
    mouse_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
    mice = []
    for cls in mouse_classes:
        x, y = place_random(grid)
        m = cls(x, y, mouse_img, skills=[])
        mice.append(m)

    ESCAPE_THRESHOLD = 200
    results = []
    step = 0
    num_mice = len(mice)
    start_time = time.time()

    # Deadlock prevention
    recent_states = []
    MAX_REPEAT = 5

    while mice and step < ESCAPE_THRESHOLD:
        # Record states for deadlock detection
        state = (
            cat_pos,
            tuple(sorted((m.x, m.y, m.strategy) for m in mice))
        )
        recent_states.append(state)
        if len(recent_states) > MAX_REPEAT:
            recent_states.pop(0)
        if len(recent_states) == MAX_REPEAT and all(s == recent_states[0] for s in recent_states):
            print(f"⚠️ Deadlock detected at step {step}. Repositioning cat.")
            cat_pos = place_random(grid)
            recent_states.clear()
            continue

        # Cat moves
        cat_pos = cat.move(cat_pos, mice, grid, grid_size)

        remaining = []
        for m in mice:
            m.age += 1

            if m.age >= ESCAPE_THRESHOLD:
                results.append({
                    'cat_strategy': cat.name,
                    'mouse_strategy': m.strategy,
                    'caught': 0,
                    'caught_time': -1,
                    'caught_seconds': -1,
                    'steps': m.age,
                    'num_mice': num_mice,
                    'map': map_name,
                })
                continue

            if (m.x, m.y) == cat_pos:
                t_now = time.time()
                results.append({
                    'cat_strategy': cat.name,
                    'mouse_strategy': m.strategy,
                    'caught': 1,
                    'caught_time': step,
                    'caught_seconds': round(t_now - start_time, 2),
                    'steps': step,
                    'num_mice': num_mice,
                    'map': map_name,
                })
                continue

            m.move(grid, grid_size, cat_pos)

            if (m.x, m.y) == cat_pos:
                t_now = time.time()
                results.append({
                    'cat_strategy': cat.name,
                    'mouse_strategy': m.strategy,
                    'caught': 1,
                    'caught_time': step,
                    'caught_seconds': round(t_now - start_time, 2),
                    'steps': step,
                    'num_mice': num_mice,
                    'map': map_name,
                })
            else:
                remaining.append(m)

        mice = remaining
        step += 1
        clock.tick(FPS)

        # Deadlock recheck (based only on position)
        state = (cat_pos, tuple(sorted((m.x, m.y) for m in mice)))
        recent_states.append(state)
        if len(recent_states) > MAX_REPEAT:
            recent_states.pop(0)
        if len(recent_states) == MAX_REPEAT and all(s == recent_states[0] for s in recent_states):
            print("⚠️ Deadlock detected. Breaking.")
            break

    # Add remaining mice as escaped
    for m in mice:
        results.append({
            'cat_strategy': cat.name,
            'mouse_strategy': m.strategy,
            'caught': 0,
            'caught_time': -1,
            'caught_seconds': -1,
            'steps': step,
            'num_mice': num_mice,
            'map': map_name,
        })

    pygame.quit()
    return results


def run_batch_experiments(num_trials=50, export_csv=True):
    cat_classes = [SmartCat, PredictiveCat, BurstMoveCat]
    all_results = []

    total_trials = len(cat_classes) * len(map_names) * num_trials
    trial_count = 0
    start_global = time.time()

    for map_name in map_names:
        for cat_cls in cat_classes:
            for trial in range(num_trials):
                start = time.time()
                print(f"🔁 Progress {trial_count + 1}/{total_trials} | Map={map_name} | Cat={cat_cls.__name__} | Trial {trial + 1}")

                game_results = run_single_game(cat_cls, map_name)
                all_results.extend(game_results)

                trial_count += 1
                duration = time.time() - start
                avg_time = (time.time() - start_global) / trial_count
                eta = avg_time * (total_trials - trial_count)
                print(f"⏱️ Trial took {duration:.2f}s | ETA: {eta / 60:.1f} min\\n")

    if export_csv:
        filename = f"experiment_results_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'cat_strategy', 'mouse_strategy', 'caught',
                'caught_time', 'caught_seconds', 'steps', 'num_mice',
                'map'
            ])
            writer.writeheader()
            writer.writerows(all_results)
        print(f"✅ Results exported to {filename}")

    return all_results
