import random

# Game Map Settings

# If using a random map, the following config is ignored (you currently use load_fixed_map())
# GRID_SIZE is useful for default window size, fallback logic, etc.
GRID_SIZE = 20         # Default value, can be overridden dynamically
CELL_SIZE = 30         # Pixel size per cell (affects rendering resolution)

# Mouse Settings

# Initial number of mice
NUM_MICE = 6

# Mouse image file prefix
MOUSE_IMAGE_PREFIX = "jerry"

# Game Control Settings

FPS = 5                     # Frame rate (frames per second)
ESCAPE_THRESHOLD = 200      # If a mouse survives more than 200 steps, it's considered escaped

# Experimental Map Settings (only used with generate_grid(...))

# Only used if generating a random grid
NUM_OBSTACLES = 120

