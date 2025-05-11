import random
from collections import deque

class Mouse:
    def __init__(self, x, y, image, strategy_name="Base", skills=None):
        self.x = x
        self.y = y
        self.image = image
        self.strategy = strategy_name
        self.age = 0
        self.prev_pos = None
        self.skills = skills or []
        self.shield = "shield" in self.skills
        self.used_teleport = False
        self.smoked = False
        self.cooldowns = {skill: 0 for skill in self.skills}
        # Loop detection: store last 6 (self_pos, cat_pos) pairs
        self._loop_history = deque(maxlen=6)

    def reduce_cooldowns(self):
        for skill in self.cooldowns:
            if self.cooldowns[skill] > 0:
                self.cooldowns[skill] -= 1

    def teleport(self, grid, grid_size):
        free = [
            (x, y) for x in range(grid_size) for y in range(grid_size)
            if grid[y][x] == 0 and (x, y) != (self.x, self.y)
        ]
        if free:
            self.x, self.y = random.choice(free)
            self.used_teleport = True

    def use_skills(self, grid, grid_size, cat_pos):
        self.reduce_cooldowns()
        self.smoked = False

        if "smoke" in self.skills and self.cooldowns.get("smoke", 0) == 0:
            self.smoked = True
            self.cooldowns["smoke"] = 3

        if "teleport" in self.skills and not self.used_teleport and self.cooldowns.get("teleport", 0) == 0:
            if random.random() < 0.1:
                self.teleport(grid, grid_size)
                self.cooldowns["teleport"] = 3

        if "shield" in self.skills and not self.shield and self.cooldowns.get("shield", 0) == 0:
            self.shield = True
            self.cooldowns["shield"] = 3

    def move(self, grid, grid_size, cat_pos):
        # 1. Loop detection: record and check current pair
        pair = ((self.x, self.y), cat_pos)
        self._loop_history.append(pair)
        if list(self._loop_history).count(pair) > 1:
            return self._break_cycle_move(grid, grid_size)

        # 2. Default random movement with skills
        self.use_skills(grid, grid_size, cat_pos)
        steps = 2 if "dash" in self.skills and self.cooldowns.get("dash", 0) == 0 and self.age % 5 == 0 else 1
        if steps == 2:
            self.cooldowns["dash"] = 3

        for _ in range(steps):
            self.move_random(grid, grid_size)

        self.age += 1
        return (self.x, self.y)

    def move_random(self, grid, grid_size):
        dirs = [(0, 1), (1, 0), (-1, 0), (0, -1)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < grid_size and 0 <= ny < grid_size and grid[ny][nx] == 0:
                self.prev_pos = (self.x, self.y)
                self.x, self.y = nx, ny
                return

    def _break_cycle_move(self, grid, grid_size):
        """
        Breaking loop logic: randomly jump 3–5 steps
        """
        steps = random.randint(3, 5)
        x, y = self.x, self.y
        for _ in range(steps):
            dirs = [(0,1),(0,-1),(1,0),(-1,0)]
            dx, dy = random.choice(dirs)
            nx, ny = x + dx, y + dy
            if 0 <= nx < grid_size and 0 <= ny < grid_size and grid[ny][nx] == 0:
                x, y = nx, ny
        # Direct jump without updating prev_pos
        self.x, self.y = x, y
        return (x, y)

    def position(self):
        return self.x, self.y


# 1. Random Mouse
class RandomMouse(Mouse):
    def __init__(self, x, y, image, skills=None):
        super().__init__(x, y, image, strategy_name="Random", skills=skills)


# 2. Distance-based RunAway Mouse
class RunAwayMouse(Mouse):
    def __init__(self, x, y, image, skills=None):
        super().__init__(x, y, image, strategy_name="RunAway", skills=skills)

    def move(self, grid, grid_size, cat_pos):
        pair = ((self.x, self.y), cat_pos)
        self._loop_history.append(pair)
        if list(self._loop_history).count(pair) > 1:
            return self._break_cycle_move(grid, grid_size)

        self.use_skills(grid, grid_size, cat_pos)
        self.reduce_cooldowns()
        dirs = [(0, 1), (1, 0), (-1, 0), (0, -1)]
        best = (self.x, self.y)
        max_dist = -1
        for dx, dy in dirs:
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < grid_size and 0 <= ny < grid_size and grid[ny][nx] == 0:
                dist = abs(nx - cat_pos[0]) + abs(ny - cat_pos[1])
                if dist > max_dist:
                    best = (nx, ny)
                    max_dist = dist
        self.prev_pos = (self.x, self.y)
        self.x, self.y = best
        self.age += 1
        return best


# 3. Smart RunAway Mouse
class SmartRunAwayMouse(Mouse):
    def __init__(self, x, y, image, skills=None):
        super().__init__(x, y, image, strategy_name="SmartRunAway", skills=skills)

    def move(self, grid, grid_size, cat_pos):
        pair = ((self.x, self.y), cat_pos)
        self._loop_history.append(pair)
        if list(self._loop_history).count(pair) > 1:
            return self._break_cycle_move(grid, grid_size)

        self.use_skills(grid, grid_size, cat_pos)
        self.reduce_cooldowns()
        dirs = [(0, 1), (1, 0), (-1, 0), (0, -1)]
        best = (self.x, self.y)
        max_score = -9999
        for dx, dy in dirs:
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < grid_size and 0 <= ny < grid_size and grid[ny][nx] == 0:
                dist = abs(nx - cat_pos[0]) + abs(ny - cat_pos[1])
                wall_penalty = sum(
                    1 for ddx, ddy in dirs
                    if 0 <= nx+ddx < grid_size and 0 <= ny+ddy < grid_size and grid[ny+ddy][nx+ddx] == 1
                )
                score = dist * 2 - wall_penalty
                if score > max_score:
                    best = (nx, ny)
                    max_score = score
        self.prev_pos = (self.x, self.y)
        self.x, self.y = best
        self.age += 1
        return best


# 4. Predictive Mouse
class PredictiveMouse(Mouse):
    def __init__(self, x, y, image, skills=None):
        super().__init__(x, y, image, strategy_name="Predictive", skills=skills)

    def move(self, grid, grid_size, cat_pos):
        pair = ((self.x, self.y), cat_pos)
        self._loop_history.append(pair)
        if list(self._loop_history).count(pair) > 1:
            return self._break_cycle_move(grid, grid_size)

        self.use_skills(grid, grid_size, cat_pos)
        self.reduce_cooldowns()
        dx = self.x - cat_pos[0]
        dy = self.y - cat_pos[1]
        pref_dirs = (
            [(1 if dx > 0 else -1, 0), (0, 1 if dy > 0 else -1)]
            if abs(dx) > abs(dy)
            else [(0, 1 if dy > 0 else -1), (1 if dx > 0 else -1, 0)]
        )
        for dx, dy in pref_dirs + [(0, 1), (1, 0), (-1, 0), (0, -1)]:
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < grid_size and 0 <= ny < grid_size and grid[ny][nx] == 0:
                self.prev_pos = (self.x, self.y)
                self.x, self.y = nx, ny
                self.age += 1
                return (nx, ny)


# 5. Corner-Hiding Mouse
class CornerMouse(Mouse):
    def __init__(self, x, y, image, skills=None):
        super().__init__(x, y, image, strategy_name="Corner", skills=skills)

    def move(self, grid, grid_size, cat_pos):
        pair = ((self.x, self.y), cat_pos)
        self._loop_history.append(pair)
        if list(self._loop_history).count(pair) > 1:
            return self._break_cycle_move(grid, grid_size)

        self.use_skills(grid, grid_size, cat_pos)
        self.reduce_cooldowns()
        dirs = [(0, 1), (1, 0), (-1, 0), (0, -1)]
        best = (self.x, self.y)
        best_score = -999
        for dx, dy in dirs:
            nx, ny = self.x + dx, self.y + dy
            if not (0 <= nx < grid_size and 0 <= ny < grid_size): continue
            if grid[ny][nx] != 0: continue
            dist_to_cat = abs(nx - cat_pos[0]) + abs(ny - cat_pos[1])
            edge_score = min(nx, grid_size - 1 - nx) + min(ny, grid_size - 1 - ny)
            wall_count = sum(
                1 for ddx, ddy in dirs
                if 0 <= nx+ddx < grid_size and 0 <= ny+ddy < grid_size and grid[ny+ddy][nx+ddx] == 1
            )
            total_score = dist_to_cat + edge_score + wall_count
            if total_score > best_score:
                best_score = total_score
                best = (nx, ny)
        self.prev_pos = (self.x, self.y)
        self.x, self.y = best
        self.age += 1
        return best


# 6. Memory Mouse
class MemoryMouse(Mouse):
    def __init__(self, x, y, image, skills=None):
        super().__init__(x, y, image, strategy_name="Memory", skills=skills)

    def move(self, grid, grid_size, cat_pos):
        pair = ((self.x, self.y), cat_pos)
        self._loop_history.append(pair)
        if list(self._loop_history).count(pair) > 1:
            return self._break_cycle_move(grid, grid_size)

        self.use_skills(grid, grid_size, cat_pos)
        self.reduce_cooldowns()
        dirs = [(0, 1), (1, 0), (-1, 0), (0, -1)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < grid_size and 0 <= ny < grid_size and grid[ny][nx] == 0:
                if (nx, ny) != self.prev_pos:
                    self.prev_pos = (self.x, self.y)
                    self.x, self.y = nx, ny
                    self.age += 1
                    return (nx, ny)
        # Fallback: fully random move
        self.move_random(grid, grid_size)
        self.age += 1
        return (self.x, self.y)

