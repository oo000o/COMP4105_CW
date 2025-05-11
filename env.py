import pygame
import os
from config import *

MOUSE_IMAGE_PREFIX = "jerry"

def load_mouse_images(folder, size):
    # Load all Jerry images from the assets folder and scale to cell size
    images = []
    for fname in sorted(os.listdir(folder)):
        if fname.startswith(MOUSE_IMAGE_PREFIX) and fname.endswith(".png"):
            img = pygame.image.load(os.path.join(folder, fname))
            img = pygame.transform.scale(img, (size, size))
            images.append(img)
    return images

def place_random(grid):
    # Randomly choose an empty cell on the map
    grid_size = len(grid)
    while True:
        x = random.randint(0, grid_size - 1)
        y = random.randint(0, grid_size - 1)
        if grid[y][x] == 0:
            return x, y

def load_fixed_map(name):
    # Load a predefined map: either 'easy' or 'hard'
    if name == "easy":
        grid = [[0] * 15 for _ in range(15)]
        for i in range(0, 15, 3):
            grid[0][i] = 1
            grid[i][0] = 1
            grid[14][i] = 1
            grid[i][14] = 1
        # Central cross obstacles
        for i in range(6, 9):
            grid[7][i] = 1
            grid[i][7] = 1
        return grid

    elif name == "hard":
        grid = [[0] * 20 for _ in range(20)]

        # Central cross (20 obstacles)
        for i in range(5, 15):
            grid[10][i] = 1
            grid[i][10] = 1

        # Diagonal blockers (~10 points)
        for i in range(4, 16, 2):
            grid[i][i] = 1
            grid[i][19 - i] = 1

        # Corner obstacle clusters (36 obstacles)
        corners = [(3, 3), (3, 15), (15, 3), (15, 15)]
        for cx, cy in corners:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    x, y = cx + dx, cy + dy
                    if 0 <= x < 20 and 0 <= y < 20:
                        grid[y][x] = 1

        # Random scattered obstacles (30–40)
        import random
        placed = 0
        while placed < 35:
            x, y = random.randint(0, 19), random.randint(0, 19)
            if grid[y][x] == 0:
                grid[y][x] = 1
                placed += 1

        return grid

    else:
        raise ValueError(f"❌ Unknown map name: {name}")

def draw(screen, grid, cat_pos, mice, cat_img):
    # Draw the map, cat, and mice on the screen
    WHITE = (255, 255, 255)
    GRAY = (150, 150, 150)
    BLACK = (0, 0, 0)
    screen.fill(WHITE)

    grid_size = len(grid)
    for y in range(grid_size):
        for x in range(grid_size):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if grid[y][x] == 1:
                pygame.draw.rect(screen, GRAY, rect)  # obstacle
            pygame.draw.rect(screen, BLACK, rect, 1)  # grid lines

    # Draw the cat
    screen.blit(cat_img, pygame.Rect(cat_pos[0]*CELL_SIZE, cat_pos[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Draw each mouse with skill indicators and cooldown values
    font = pygame.freetype.SysFont(None, 14)

    for m in mice:
        screen.blit(m.image, pygame.Rect(m.x * CELL_SIZE, m.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        center = (m.x * CELL_SIZE + CELL_SIZE // 2, m.y * CELL_SIZE + CELL_SIZE // 2)

        if "dash" in m.skills:
            pygame.draw.circle(screen, (255, 255, 0), center, 4)
            font.render_to(screen, (center[0] - 6, center[1] - 6), str(m.cooldowns["dash"]), (0, 0, 0))

        if "shield" in m.skills:
            pygame.draw.circle(screen, (0, 150, 255), center, 6, 1)
            font.render_to(screen, (center[0] - 6, center[1] - 6), str(m.cooldowns["shield"]), (0, 0, 0))

        if "teleport" in m.skills:
            pygame.draw.circle(screen, (255, 0, 255), center, 4)
            font.render_to(screen, (center[0] - 6, center[1] - 6), str(m.cooldowns["teleport"]), (0, 0, 0))

        if "smoke" in m.skills:
            pygame.draw.circle(screen, (100, 100, 100), center, 6, 1)
            font.render_to(screen, (center[0] - 6, center[1] - 6), str(m.cooldowns["smoke"]), (0, 0, 0))

    pygame.display.flip()

def move_towards(src, target, grid):
    # Move the cat one step closer to the target mouse
    dx = target[0] - src[0]
    dy = target[1] - src[1]
    step = (0, 0)
    if abs(dx) > abs(dy):
        step = (1 if dx > 0 else -1, 0)
    else:
        step = (0, 1 if dy > 0 else -1)
    new_x = src[0] + step[0]
    new_y = src[1] + step[1]
    if 0 <= new_x < len(grid) and 0 <= new_y < len(grid) and grid[new_y][new_x] != 1:
        return (new_x, new_y)
    return src
