import random
from collections import deque
from utils.smart_cat_utils import smart_move_cat

class BaseCat:
    def __init__(self, name="BaseCat"):
        self.name = name
        # Loop detection: store recent (cat_pos, mice_positions) tuples
        self._loop_history = deque(maxlen=6)

    def _unpack_grid_size(self, grid_size):
        # Support grid_size as int or (w, h)
        if isinstance(grid_size, int):
            return grid_size, grid_size
        return grid_size

    def _break_cycle_move(self, cat_pos, grid, grid_size):
        # Break loop: try moving randomly to any valid adjacent tile
        w, h = self._unpack_grid_size(grid_size)
        dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = cat_pos[0] + dx, cat_pos[1] + dy
            if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] == 0:
                return (nx, ny)
        return cat_pos

    def move(self, cat_pos, mice, grid, grid_size):
        # Default: do not move
        return cat_pos


class SmartCat(BaseCat):
    # SmartCat: uses BFS to chase the closest mouse
    def __init__(self):
        super().__init__("SmartCat")

    def move(self, cat_pos, mice, grid, grid_size):
        w, h = self._unpack_grid_size(grid_size)

        # Loop detection
        mice_pos = tuple((m.x, m.y) for m in mice)
        current = (cat_pos, mice_pos)
        self._loop_history.append(current)
        if list(self._loop_history).count(current) > 1:
            return self._break_cycle_move(cat_pos, grid, grid_size)

        if not mice:
            return cat_pos

        # Chase the nearest mouse
        target = min(mice, key=lambda m: abs(cat_pos[0] - m.x) + abs(cat_pos[1] - m.y))
        return smart_move_cat(cat_pos, (target.x, target.y), grid, (w, h))


class PredictiveCat(BaseCat):
    # PredictiveCat: predicts the next position of the mouse and intercepts it
    def __init__(self):
        super().__init__("PredictiveCat")

    def move(self, cat_pos, mice, grid, grid_size):
        w, h = self._unpack_grid_size(grid_size)

        # Loop detection
        mice_pos = tuple((m.x, m.y) for m in mice)
        current = (cat_pos, mice_pos)
        self._loop_history.append(current)
        if list(self._loop_history).count(current) > 1:
            return self._break_cycle_move(cat_pos, grid, grid_size)

        if not mice:
            return cat_pos

        # Predict the mouse’s movement and go to that location
        best = cat_pos
        min_dist = float('inf')
        for m in mice:
            dx = m.x - cat_pos[0]
            dy = m.y - cat_pos[1]

            if abs(dx) > abs(dy):
                pred = (m.x + (1 if dx > 0 else -1), m.y)
            else:
                pred = (m.x, m.y + (1 if dy > 0 else -1))

            px, py = pred
            if 0 <= px < w and 0 <= py < h and grid[py][px] == 0:
                dist = abs(px - cat_pos[0]) + abs(py - cat_pos[1])
                if dist < min_dist:
                    min_dist = dist
                    best = pred

        return smart_move_cat(cat_pos, best, grid, (w, h))


class BurstMoveCat(BaseCat):
    # BurstMoveCat: dashes every 10 steps (takes two steps)
    def __init__(self, burst_interval=10):
        super().__init__("BurstMoveCat")
        self.step_count = 0
        self.burst_interval = burst_interval

    def move(self, cat_pos, mice, grid, grid_size):
        w, h = self._unpack_grid_size(grid_size)

        # Loop detection
        mice_pos = tuple((m.x, m.y) for m in mice)
        current = (cat_pos, mice_pos)
        self._loop_history.append(current)
        if list(self._loop_history).count(current) > 1:
            return self._break_cycle_move(cat_pos, grid, grid_size)

        if not mice:
            return cat_pos

        self.step_count += 1

        # Chase the nearest mouse
        target = min(mice, key=lambda m: abs(cat_pos[0] - m.x) + abs(cat_pos[1] - m.y))

        # First step
        pos1 = smart_move_cat(cat_pos, (target.x, target.y), grid, (w, h))

        # Second step if burst is due
        if self.step_count % self.burst_interval == 0:
            pos2 = smart_move_cat(pos1, (target.x, target.y), grid, (w, h))
            return pos2
        return pos1


def create_random_cat(exclude=None):
    # Randomly select a cat
    exclude = exclude or []
    CatClasses = [SmartCat, PredictiveCat, BurstMoveCat]
    choices = [c for c in CatClasses if c.__name__ not in exclude]
    return random.choice(choices)()
