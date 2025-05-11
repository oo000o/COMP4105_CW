import random
import numpy as np

class QLearningMouse:
    def __init__(self, x, y, image, q_table, alpha=0.1, gamma=0.9, epsilon=0.2):
        self.x = x
        self.y = y
        self.position = (x, y)
        self.image = image
        self.q_table = q_table
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.age = 0
        self.strategy = "QLearning"
        self.training = False  # Set to False during evaluation
        self.prev_state = None
        self.prev_action = None

    def get_state(self, grid, cat_pos):
        return (*self.position, *cat_pos)

    def get_valid_actions(self, grid, grid_size):
        dirs = [(0, 1), (1, 0), (-1, 0), (0, -1)]
        valid = []
        for dx, dy in dirs:
            nx, ny = self.position[0] + dx, self.position[1] + dy
            if 0 <= nx < grid_size and 0 <= ny < grid_size and grid[ny][nx] == 0:
                valid.append((dx, dy))
        return valid

    def choose_action(self, state, actions):
        if random.random() < self.epsilon:
            return random.choice(actions)
        q_values = [self.q_table.get((state, a), 0) for a in actions]
        return actions[np.argmax(q_values)]

    def update_q(self, reward, new_state, new_actions):
        if self.prev_state is None or self.prev_action is None:
            return
        prev_q = self.q_table.get((self.prev_state, self.prev_action), 0)
        future_q = max([self.q_table.get((new_state, a), 0) for a in new_actions], default=0)
        new_q = prev_q + self.alpha * (reward + self.gamma * future_q - prev_q)
        self.q_table[(self.prev_state, self.prev_action)] = new_q

    def move(self, grid, grid_size, cat_pos):
        self.age += 1
        state = self.get_state(grid, cat_pos)
        actions = self.get_valid_actions(grid, grid_size)
        if not actions:
            return
        action = self.choose_action(state, actions)
        new_x = self.position[0] + action[0]
        new_y = self.position[1] + action[1]
        self.position = (new_x, new_y)
        self.x, self.y = new_x, new_y

        # Update Q-table
        if self.training:
            reward = -1 if self.position == cat_pos else 0.1
            new_state = self.get_state(grid, cat_pos)
            new_actions = self.get_valid_actions(grid, grid_size)
            self.update_q(reward, new_state, new_actions)
            self.prev_state = state
            self.prev_action = action
