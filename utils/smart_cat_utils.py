from collections import deque


def _unpack_grid_size(grid_size):
    """
    Support grid_size being either a single int (square grid),
    or a tuple of (width, height).
    """
    if isinstance(grid_size, int):
        return grid_size, grid_size
    return grid_size


def bfs_path(grid, start, goal, grid_size):
    """
    Perform BFS to find a path from start to goal on the grid.

    Parameters:
        grid: 2D list grid[y][x], where 1 = wall, 0 = walkable
        start: (x, y) starting position
        goal: (x, y) target position
        grid_size: int or tuple (width, height)

    Returns:
        The next step coordinate (x, y) to move toward goal.
    """
    w, h = _unpack_grid_size(grid_size)

    # If goal is invalid or blocked, do not move
    if not (0 <= goal[0] < w and 0 <= goal[1] < h) or grid[goal[1]][goal[0]] == 1:
        return start

    visited = set([start])
    queue = deque([[start]])

    while queue:
        path = queue.popleft()
        x, y = path[-1]

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy

            # Boundary check
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            # Wall check
            if grid[ny][nx] == 1:
                continue
            # Already visited
            if (nx, ny) in visited:
                continue

            new_path = path + [(nx, ny)]

            # Reached goal → return second step in path
            if (nx, ny) == goal:
                return new_path[1]

            visited.add((nx, ny))
            queue.append(new_path)

    # No path found → stay in place
    return start


def smart_move_cat(cat_pos, target_pos, grid, grid_size):
    """
    Return the next position for the cat to move toward the target using BFS.

    Parameters:
        cat_pos: current position of the cat (x, y)
        target_pos: position to chase (x, y)
        grid: 2D map
        grid_size: int or tuple (width, height)
    """
    return bfs_path(grid, cat_pos, target_pos, grid_size)

