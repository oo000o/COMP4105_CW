import pygame
import sys
import random
from config import *
from env import *
from utils.smart_cat_utils import smart_move_cat
from cat_agent import create_random_cat
from agent import (
    RandomMouse, RunAwayMouse, SmartRunAwayMouse,
    PredictiveMouse, CornerMouse, MemoryMouse
)
from experiment1 import run_batch_experiments

print(f"Game started with {NUM_MICE} mice.")

# Load map
map_name = random.choice(["easy", "hard"])
grid = load_fixed_map(map_name)
grid_size = len(grid)

# Initialize window and clock
pygame.init()
screen = pygame.display.set_mode((grid_size * CELL_SIZE, grid_size * CELL_SIZE))
pygame.display.set_caption("Modular Cat vs Mice")
clock = pygame.time.Clock()

# === Load images ===
cat_img = pygame.image.load("assets/tom.png")
cat_img = pygame.transform.scale(cat_img, (CELL_SIZE, CELL_SIZE))
mouse_imgs = load_mouse_images("assets", CELL_SIZE)

# Initialize map and entities
cat_agent = create_random_cat()
cat_pos = place_random(grid)
print(f"🐱 Cat strategy: {cat_agent.name}")

mouse_classes = [
    RandomMouse,
    RunAwayMouse,
    SmartRunAwayMouse,
    PredictiveMouse,
    CornerMouse,
    MemoryMouse
]

possible_skills = ["dash", "shield", "teleport", "smoke", "none"]
mice = []
mouse_imgs = load_mouse_images("assets", CELL_SIZE)
for i in range(NUM_MICE):
    index = i % len(mouse_classes)
    MouseClass = mouse_classes[index]
    img = mouse_imgs[index]
    assigned_skill = random.choice(possible_skills[:-1]) if random.random() < 1.0 else None
    skills = [assigned_skill] if assigned_skill else []
    x, y = place_random(grid)
    m = MouseClass(x, y, img, skills=skills)
    mice.append(m)
    print(f"🧀 Created {MouseClass.__name__} at ({x}, {y}) with jerry{index+1}.png | Skills: {skills}")

# Tracking
step = 0
death_log = []
escaped_log = []
ESCAPE_THRESHOLD = 600

# Deadlock detection
recent_states = []
MAX_REPEAT = 3

# Main loop

def main_loop():
    global cat_pos, mice, step, cat_agent, death_log, escaped_log
    running = True
    escaped_log = []
    ESCAPE_THRESHOLD = 200
    MAX_REPEAT = 5
    recent_states = []

    while running:
        draw(screen, grid, cat_pos, mice, cat_img)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Record current state for deadlock detection
        current_state = (cat_pos, tuple(sorted((m.x, m.y) for m in mice)))
        recent_states.append(current_state)
        if len(recent_states) > MAX_REPEAT:
            recent_states.pop(0)

        # Check for repeated states (deadlock)
        if len(recent_states) == MAX_REPEAT and all(s == recent_states[0] for s in recent_states):
            print("⚠️ Deadlock detected.")

            prev_name = cat_agent.name
            cat_agent = create_random_cat(exclude=[prev_name])
            cat_pos = place_random(grid)

            # Shuffle mice to break loop
            random.shuffle(mice)
            for m in mice:
                m.x, m.y = place_random(grid)

            print(f"🚨 Cat strategy switched from {prev_name} to {cat_agent.name} to break deadlock.")
            recent_states.clear()
            continue

        # Move the cat
        if mice:
            cat_pos = cat_agent.move(cat_pos, mice, grid, grid_size)

        # Move the mice & check status
        remaining = []
        for m in mice:
            m.age += 1
            caught = False

            # Step 1: Check for escape
            if m.age >= ESCAPE_THRESHOLD:
                print(f"🕳️  A {m.strategy} mouse escaped at ({m.x}, {m.y}) after {m.age} steps!")
                escaped_log.append((m.strategy, m.age))
                continue

            # Step 2: Check if caught before move
            if (m.x, m.y) == cat_pos:
                if getattr(m, "smoked", False):
                    print(f"😶 {m.strategy} mouse evaded with smoke!")
                elif getattr(m, "shield", False):
                    print(f"🛡️ {m.strategy} mouse blocked the cat with shield!")
                    m.shield = False
                else:
                    print(f"🐱 Cat caught a {m.strategy} mouse at ({m.x}, {m.y})")
                    death_log.append((m.strategy, step))
                    caught = True

            # Step 3: Move
            if not caught:
                m.move(grid, grid_size, cat_pos)

                # Step 4: Check if caught after move
                if (m.x, m.y) == cat_pos:
                    print(f"🐱 Cat caught a {m.strategy} mouse at ({m.x}, {m.y})")
                    death_log.append((m.strategy, step))
                else:
                    remaining.append(m)

        mice = remaining

        if not mice:
            print("🎉 All mice have been caught. Cat wins!")
            running = False

        clock.tick(FPS)
        step += 1

    # Summary
    print("\n--- Survival Summary ---")
    for strategy, t in death_log:
        print(f"{strategy} mouse survived {t} steps.")
    print("\n--- Escape Summary ---")
    for strategy, t in escaped_log:
        print(f"{strategy} mouse escaped after {t} steps.")
    pygame.quit()
    sys.exit()

# Start
if __name__ == "__main__":
    main_loop()
    # for experiment1
    # run_batch_experiments(num_trials=50, export_csv=True)

