import random
import pickle
import time
from collections import defaultdict
from env import load_fixed_map, place_random
from cat_agent import SmartCat, PredictiveCat, BurstMoveCat

# Q-learning parameters
ACTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Down, Up, Right, Left
Q = defaultdict(lambda: [0.0] * len(ACTIONS))
alpha = 0.1
gamma = 0.95
epsilon = 0.2
EPISODES = 5000
ESCAPE_THRESHOLD = 200

def get_state(mouse, cat, grid):
    # State: relative position + wall surroundings
    dx = max(-5, min(5, mouse[0] - cat[0]))
    dy = max(-5, min(5, mouse[1] - cat[1]))
    wall_info = []
    for dx2, dy2 in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = mouse[0] + dx2, mouse[1] + dy2
        if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid):
            wall_info.append(grid[ny][nx])
        else:
            wall_info.append(1)
    return (dx, dy, *wall_info)

def choose_action(state):
    # Epsilon-greedy action selection
    if random.random() < epsilon:
        return random.randint(0, len(ACTIONS) - 1)
    return max(range(len(ACTIONS)), key=lambda a: Q[state][a])

def is_valid(pos, grid):
    # Check if position is walkable
    x, y = pos
    return 0 <= x < len(grid[0]) and 0 <= y < len(grid) and grid[y][x] == 0

# Initialize environment settings
cat_classes = [SmartCat, PredictiveCat, BurstMoveCat]
map_names = ["easy", "hard"]
start_time = time.time()

for episode in range(EPISODES):
    # Random map and cat strategy
    map_name = random.choice(map_names)
    grid = load_fixed_map(map_name)
    grid_size = len(grid)
    cat = random.choice(cat_classes)()
    cat_pos = place_random(grid)
    mouse_pos = place_random(grid)

    steps = 0
    while steps < ESCAPE_THRESHOLD:
        state = get_state(mouse_pos, cat_pos, grid)
        action_idx = choose_action(state)
        dx, dy = ACTIONS[action_idx]
        next_mouse = (mouse_pos[0] + dx, mouse_pos[1] + dy)

        if not is_valid(next_mouse, grid):
            next_mouse = mouse_pos  # Stay in place if hit a wall

        # Simulate cat movement using dummy mouse
        dummy_mouse = type("DummyMouse", (), {"x": next_mouse[0], "y": next_mouse[1]})()
        cat_pos = cat.move(cat_pos, [dummy_mouse], grid, grid_size)

        next_state = get_state(next_mouse, cat_pos, grid)

        # Reward function
        if next_mouse == cat_pos:
            reward = -10
            done = True
        else:
            dist_old = abs(mouse_pos[0] - cat_pos[0]) + abs(mouse_pos[1] - cat_pos[1])
            dist_new = abs(next_mouse[0] - cat_pos[0]) + abs(next_mouse[1] - cat_pos[1])
            reward = 1 if dist_new > dist_old else 0.5
            done = False

        # Q-learning update
        old_q = Q[state][action_idx]
        max_next_q = max(Q[next_state])
        Q[state][action_idx] = old_q + alpha * (reward + gamma * max_next_q - old_q)

        mouse_pos = next_mouse
        steps += 1

        if done:
            break

    # Progress logging
    if (episode + 1) % 100 == 0:
        elapsed = time.time() - start_time
        avg_time = elapsed / (episode + 1)
        eta = avg_time * (EPISODES - episode - 1)
        print(f"✅ Episode {episode + 1}/{EPISODES} | ⏱️ Avg: {avg_time:.2f}s | ETA: {eta / 60:.1f} min")

# Save Q-table
with open("q_table.pkl", "wb") as f:
    pickle.dump(dict(Q), f)

print("🎉 Training finished! Q-table saved to q_table.pkl")

