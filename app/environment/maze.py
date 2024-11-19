import gymnasium as gym
import numpy as np
from gymnasium import spaces
from app.services.map_services import find_points, get_min_steps, increment_position

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
        """
        Initializes the maze environment.

        Args:
            grid (list): The grid representing the maze.
            start_point (tuple): The starting position of the agent.
            exit_point (tuple): The exit point in the maze.
        """
        super().__init__()

        self.grid = np.array(grid)
        self.nrow, self.ncol = np.shape(self.grid)
        self.start_point, self.exit_point = find_points(grid, start_point, exit_point)
        self.minimum_steps = len(get_min_steps(self.grid)) - 1
        self.maximum_steps = self.size() * 10  # Maximum steps to avoid losing
        self.action_space = spaces.Discrete(4)

        # Define the observation space (current position in the maze)
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, 0]),
            high=np.array([self.size() - 1, self.size() - 1, self.size() - 1, self.size() - 1]),
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
        Returns the size of the maze.

        Returns:
            tuple: The shape of the grid.
        """
        return self.nrow if self.nrow == self.ncol else np.shape(self.grid)

    def reset(self, *, seed=None, return_info=False, options=None):
        """
        Resets the environment to its initial state.

        Args:
            seed (int): A seed for the random number generator.
            return_info (bool): Whether to return additional information.
            options (dict): Additional options for resetting the environment.

        Returns:
            tuple: A tuple containing the initial observation and additional info.
        """
        if seed is not None:
            np.random.seed(seed)
        self.current_state = self.start_point
        self.total_steps_performed = 0
        self.reward = 0
        self.done = False
        self.win = False
        self.lose_by_mine = False
        self.lose_by_steps = False
        self.final_position = None
        self.episode_result = None

        return self._obs_space(), {}

    def _obs_space(self):
        """
        Constructs and returns the observation state: [agent_row_pos, agent_col_pos, exit_row_pos, exit_col_pos].

        Returns:
            numpy.ndarray: The observation state as an array.
        """
        obs1 = np.array(self.current_state)
        obs2 = np.array(self.exit_point)
        total_obs = np.concatenate([obs1, obs2])
        return np.array(total_obs, dtype=np.int32)

    def step(self, action):
        """
        Executes one step in the environment based on the given action.

        Args:
            action (int): The action taken by the agent.

        Returns:
            tuple: The next observation, the reward, whether the episode is done, and additional info.
        """
        self.total_steps_performed += 1
        row, col = self.current_state
        new_state = self._update_state_and_reward(row, col, action)
        self.current_state = new_state
        if self.lose_by_mine or self.done:
            self.final_position = self.current_state
        return self._obs_space(), self.reward, self.done, False, {}

    def _update_state_and_reward(self, row, col, action):
        """
        Updates the state and reward based on the action.

        Args:
            row (int): The current row position.
            col (int): The current column position.
            action (int): The action taken by the agent.

        Returns:
            tuple: The new state after taking the action.
        """
        new_row, new_col = increment_position(row, col, action)

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
        """
        Returns the current state of the maze with the agent's position marked.

        Returns:
            list: The flattened maze with the agent's position marked as `AGENT`.
        """
        maze_render = np.copy(self.grid)
        row, col = self.current_state
        maze_render[row, col] = AGENT
        return maze_render.flatten().tolist()

    def render(self):
        """
        Renders the current maze state for human visualization.
        """
        maze_render = self.get_current_map_state()
        print(np.array(maze_render).reshape(self.nrow, self.ncol))

