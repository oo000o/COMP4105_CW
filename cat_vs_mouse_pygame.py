import pygame
import random
import os
import sys

# --- Configuration ---
GRID_SIZE = 20
CELL_SIZE = 30
SCREEN_SIZE = GRID_SIZE * CELL_SIZE
NUM_OBSTACLES = 40

WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
BLACK = (0, 0, 0)

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("Cat vs Mice")
clock = pygame.time.Clock()

# --- Load images ---
def load_mouse_images(folder, size):
    images = []
    for fname in sorted(os.listdir(folder)):
        if fname.startswith("jerry") and fname.endswith(".png"):
            img = pygame.image.load(os.path.join(folder, fname))
            img = pygame.transform.scale(img, (size, size))
            images.append(img)
    return images

cat_img = pygame.image.load("assets/tom.png")
cat_img = pygame.transform.scale(cat_img, (CELL_SIZE, CELL_SIZE))
mouse_imgs = load_mouse_images("assets", CELL_SIZE)

# --- Initialize map ---
EMPTY = 0
OBSTACLE = 1
grid = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

def place_random():
    while True:
        x = random.randint(0, GRID_SIZE - 1)
        y = random.randint(0, GRID_SIZE - 1)
        if grid[y][x] == EMPTY:
            return x, y

# Place obstacles
for _ in range(NUM_OBSTACLES):
    x, y = place_random()
    grid[y][x] = OBSTACLE

cat_pos = place_random()

# Mouse class
class Mouse:
    id_counter = 0  # Global ID counter
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.age = 0
        self.id = Mouse.id_counter
        Mouse.id_counter += 1

    def move_random(self):
        dirs = [(0, 1), (1, 0), (-1, 0), (0, -1)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and grid[ny][nx] == EMPTY:
                self.x, self.y = nx, ny
                return

mice = []
max_mice = min(len(mouse_imgs), 10)
for i in range(max_mice):
    x, y = place_random()
    mice.append(Mouse(x, y, mouse_imgs[i]))

# Cat movement toward a target
def move_towards(src, target):
    dx = target[0] - src[0]
    dy = target[1] - src[1]
    step = (0, 0)
    if abs(dx) > abs(dy):
        step = (1 if dx > 0 else -1, 0)
    else:
        step = (0, 1 if dy > 0 else -1)
    new_x = src[0] + step[0]
    new_y = src[1] + step[1]
    if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE and grid[new_y][new_x] != OBSTACLE:
        return (new_x, new_y)
    return src

# Draw the grid and all entities
def draw():
    screen.fill(WHITE)
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if grid[y][x] == OBSTACLE:
                pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)
    screen.blit(cat_img, pygame.Rect(cat_pos[0]*CELL_SIZE, cat_pos[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
    for m in mice:
        screen.blit(m.image, pygame.Rect(m.x * CELL_SIZE, m.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.display.flip()

# Main loop
running = True
step = 0
while running:
    draw()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Cat chases the closest mouse
    if mice:
        target_mouse = min(mice, key=lambda m: abs(cat_pos[0] - m.x) + abs(cat_pos[1] - m.y))
        cat_pos = move_towards(cat_pos, (target_mouse.x, target_mouse.y))

    remaining_mice = []
    for m in mice:
        m.age += 1
        if (m.x, m.y) == cat_pos:
            print(f"🐱 Step {step}: Caught Mouse#{m.id} at ({m.x}, {m.y}), survived {m.age} steps.")
        else:
            m.move_random()
            if (m.x, m.y) != cat_pos:
                remaining_mice.append(m)
            else:
                print(f"🐱 Step {step}: Caught Mouse#{m.id} at ({m.x}, {m.y}) after moving, survived {m.age} steps.")

    mice = remaining_mice
    if not mice:
        print(f"🎉 All mice have been caught in {step} steps. Cat wins!")
        running = False

    clock.tick(5)
    step += 1

pygame.quit()
sys.exit()
