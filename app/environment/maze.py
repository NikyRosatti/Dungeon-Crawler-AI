"""
This module defines a maze environment for reinforcement learning using Gym.
The environment allows the agent to navigate through a maze, avoiding walls,
finding the exit, and dealing with mines.
"""
import gymnasium as gym
import numpy as np
from gymnasium import spaces

from app.services.map_services import (
    find_points,
    get_min_steps,
    increment_position,
)


# Possible movements: left, down, right, up
LEFT = 0
DOWN = 1
RIGHT = 2
UP = 3

# Objects present in each cell of the grid
AGENT = -1
FLOOR = 0
WALL = 1
INITIAL_DOOR = 2
EXIT_DOOR = 3
MINE = 4


class Maze(gym.Env):
    """
    A maze environment for reinforcement learning using Gym.

    The agent navigates a grid, avoiding walls, finding the exit, and potentially
    encountering mines. The agent is rewarded or penalized based on its actions.
    """

    metadata = {"render_modes": ["human"], "render_fps": 30}

    def __init__(self, grid, start_point=None, exit_point=None):
        super().__init__()

        self.grid = np.array(grid)
        self.nrow, self.ncol = np.shape(self.grid)
        self.start_point, self.exit_point = find_points(
            grid, start_point, exit_point)
        self.minimum_steps = len(get_min_steps(self.grid)) - 1
        # Maximum number of steps to be taken:
        # When the agent makes (Maze.size() * 10) actions (steps), it ends (losing).
        self.maximum_steps = self.size() * 10
        self.action_space = spaces.Discrete(4)

        # Define the observation space: current position in the maze
        # The observation will be the coordinate (row, column), represented as a tuple
        # low = Lower limits of positions
        # high = Upper limits of positions
        # dtype = The type that the observations belong to
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, 0]),
            high=np.array(
                [self.size() - 1, self.size() - 1, self.size() - 1, self.size() - 1]
            ),
            dtype=np.int32,
        )

        # Initial states
        self.current_state = self.start_point
        self.total_steps_performed = 0
        self.reward = 0
        self.done = False
        self.win = False
        self.lose_by_mine = False
        self.lose_by_steps = False
        self.final_position = None
        self.episode_result = None

    def size(self):
        """ 
        It returns the size of the maze

        """
        return self.nrow if self.nrow == self.ncol else np.shape(self.grid)

    def reset(self, *, seed=None, return_info=False, options=None):
        """
        Reset the enviroment

        """
        if seed is not None:
            np.random.seed(seed)
        # Initial states
        self.current_state = self.start_point
        self.total_steps_performed = 0
        self.reward = 0
        self.done = False
        self.win = False
        self.lose_by_mine = False
        self.lose_by_steps = False

        return self._obs_space(), {}

    def _obs_space(self):
        """
        Returns the current observation state of the agent in the maze.

        The observation is a combination of the agent's position and the exit's position.
        """
        obs1 = np.array(self.current_state)
        obs2 = np.array(self.exit_point)
        total_obs = np.concatenate([obs1, obs2])
        return np.array(total_obs, dtype=np.int32)

    def step(self, action):
        self.total_steps_performed += 1
        row, col = self.current_state
        new_state = self._update_state_and_reward(row, col, action)
        self.current_state = new_state
        if self.lose_by_mine or self.done:
            self.final_position = self.current_state
        # truncation=False as the time limit is handled by the TimeLimit wrapper added during make
        return self._obs_space(), self.reward, self.done, False, {}

    def _update_state_and_reward(self, row, col, action):
        new_row, new_col = increment_position(row, col, action)

        # If the new position goes out of bounds or its a wall, do not allow the movement
        if (
            new_row < 0
            or new_row >= self.size()
            or new_col < 0
            or new_col >= self.size()
            or self.grid[new_row, new_col] == WALL
        ):
            self.reward -= 1
            new_state = (row, col)  # Keep the current position
        else:
            new_state = (new_row, new_col)

        new_row, new_col = new_state
        new_cell_value = self.grid[new_row, new_col]

        if new_cell_value == MINE:
            self.reward = -100
            self.lose_by_mine = True
        if new_cell_value == EXIT_DOOR:
            self.reward += 100
            self.win = True
        if new_cell_value == FLOOR:
            self.reward -= 0.1
        if self.total_steps_performed >= self.maximum_steps:
            self.reward -= 20
            self.lose_by_steps = True

        self.done = self.lose_by_mine or self.lose_by_steps or self.win

        if self.done:
            self.episode_result = {
                "win": self.win,
                "lose_by_mine": self.lose_by_mine,
                "lose_by_steps": self.lose_by_steps
            }
        return new_state

    def get_current_map_state(self):
        maze_render = np.copy(self.grid)
        row, col = self.current_state
        maze_render[row, col] = AGENT
        return maze_render.flatten().tolist()
