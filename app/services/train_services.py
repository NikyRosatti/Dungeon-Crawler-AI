"""
This module contains services related to training a reinforcement learning model
for a maze environment, including the setup of training, observation formatting, and
real-time training status updates.
"""



import json
import os
import time
from flask import session
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from app import socketio
from app.environment.maze import Maze
from app.models import User, MazeBd, db
from app.services.map_services import action_to_string


running_tests = {}


def train_model(maze_id):
    """
    Trains a reinforcement learning model using the PPO algorithm in the given maze environment.
    Outputs the training progress and saves the model at each iteration.

    Parameters:
        maze_id (int): The ID of the maze for which the model is being trained.
    """
    maze = MazeBd.query.filter_by(id=maze_id).first()
    grid1 = json.loads(maze.grid)
    size = maze.maze_size
    grid = [grid1[i: i + size] for i in range(0, len(grid1), size)]

    log_dir = os.path.join("app", "saved_models", "logs", f"{maze_id}")
    os.makedirs(log_dir, exist_ok=True)

    num_envs = 5
    env = DummyVecEnv([lambda: Maze(grid) for _ in range(num_envs)])

    model_path = os.path.join(
        "app", "saved_models", "trained_models_per_id", str(maze_id), ""
    )
    os.makedirs(model_path, exist_ok=True)

    try:
        env = VecNormalize.load(load_path=model_path +
                                "norm_env.pkl", venv=env)
        print("TrainEnv: Retraining the environment")
    except FileNotFoundError:
        env = VecNormalize(env, norm_obs=False,
                           norm_reward=True, clip_obs=10.0)
        print("TrainEnv: Creating the environment")

    try:
        model = PPO.load(path=model_path + "ppo.zip", env=env)
        print("TrainModel: Retraining the model")
    except FileNotFoundError:
        model = PPO("MlpPolicy", env=env, verbose=0, tensorboard_log=log_dir)
        print("TrainModel: Creating the model")

    print("Training started")
    timesteps = 10000
    iterations_per_learning = 10
    for i in range(iterations_per_learning):
        print(f"Training iteration {i+1}!")
        model.learn(
            total_timesteps=timesteps, reset_num_timesteps=False, progress_bar=True
        )
        # Calcular el progreso
        progress = ((i + 1) / iterations_per_learning) * 100
        print(f"Progress: {progress:.2f}%")

        # Emitir progreso a todas las páginas conectadas
        yield {"progress": progress}
        model.save(model_path + "ppo.zip")
    print(f"Model {model_path} saved successfully")
    env.save(model_path + "norm_env.pkl")
    print("Environments saved successfully")
    print("End of training")


def run_training_test(env, model, maze_id, maze, size):
    """Ejecuta la prueba de entrenamiento y emite el estado del mapa en tiempo real."""
    global running_tests

    print(
        f"Minimum steps required to solve the maze: {env.envs[0].minimum_steps}")

    user = User.query.get(session["user_id"])
    env.training = False
    env.norm_reward = False
    obs = env.reset()
    steps = 0
    while steps < env.envs[0].maximum_steps:
        steps += 1
        print(f"Steps: {steps}")

        # Si se ha solicitado detener la prueba
        if not running_tests.get(maze_id):
            print(f"Test stopped for maze_id {maze_id}")
            socketio.emit("training_status", {"status": "stopped"})
            running_tests.pop(maze_id, None)
            break

        action, _ = model.predict(obs)
        print(
            f"  Action according to the prediction: {action_to_string(action)}")
        obs, reward, done, _ = env.step(action)
        print(
            f"  Observation after the step: {obs_to_string(obs)}"
            + f"  Reward: {reward}, Done: {done}"
        )

        current_map_state = env.envs[0].get_current_map_state()
        socketio.emit("map", current_map_state)
        time.sleep(0.05)

        if done:
            win = env.envs[0].episode_result.get("win")
            lose_by_mine = env.envs[0].episode_result.get("lose_by_mine")
            lose_by_steps = env.envs[0].episode_result.get("lose_by_steps")
            if win:
                print("Maze solved")
                socketio.emit("finish_map")
                if maze not in user.completed_dungeons:
                    user.completed_dungeons.append(maze)
                    new_points = 0
                    if env.envs[0].minimum_steps == steps:
                        user.points += size + steps
                        new_points += size + steps
                    else:
                        user.points += size
                        new_points += size
                    db.session.commit()
                    socketio.emit("training_status", {"status": "finished"})
                    socketio.emit("win", {"points": new_points})
                    print(
                        f"User {user.username} completed the maze {maze_id}.")
                else:
                    print(
                        f"The user {user.username} already completed this maze.")
                socketio.emit("training_status", {"status": "finished"})

            if lose_by_mine:
                pos = env.envs[0].final_position
                socketio.emit("lose_by_mine", {"pos": pos})
                print("You agent died brutally when stepped in a mine")
                print(f"{pos}")

            if lose_by_steps:
                max_steps = env.envs[0].maximum_steps
                print(
                    f"Your agent could not complete the maze in {max_steps} steps!!")
            break

        if env.envs[0].lose_by_mine | env.envs[0].lose_by_steps:
            socketio.emit("lose")

    # Eliminar la prueba de la lista de ejecuciones
    running_tests.pop(maze_id, None)


def setup_environment(grid, maze_id):
    """
    Sets up the training environment and loads the PPO model.

    Parameters:
        grid: The maze grid.
        maze_id (int): The ID of the maze.

    Returns:
        env: The environment for training.
        model: The PPO model.
    """
    vec_norm_path = os.path.join(
        "app", "saved_models", "trained_models_per_id", str(
            maze_id), "norm_env.pkl"
    )
    model_to_load = os.path.join(
        "app", "saved_models", "trained_models_per_id", str(maze_id), "ppo.zip"
    )

    env = DummyVecEnv([lambda: Maze(grid)])
    try:
        env = VecNormalize.load(load_path=vec_norm_path, venv=env)
        print(f"Loading the environment {vec_norm_path}")
    except FileNotFoundError:
        print("Vectorized environment not found, loading a generic one")
        env = VecNormalize(env, norm_obs=False,
                           norm_reward=True, clip_obs=10.0)

    try:
        model = PPO.load(model_to_load, env=env)
        print(f"Loading the file {model_to_load}")
    except FileNotFoundError:
        print("Playing without a trained model!")
        model = PPO("MlpPolicy", env=env)

    return env, model


def obs_to_string(obs):
    """
    String representation of the observation space of the environment.

    Parameters:
        obs (VecEnvObs | np.array): The observation space.

    Returns:
        str: Agent position (X, Y) and exit position (X, Y).
    """
    obs = obs[0]
    x_agent = obs[0]
    y_agent = obs[1]
    x_exit_door = obs[2]
    y_exit_door = obs[3]
    s = f"[X_Agent: {x_agent}, Y_Agent: {y_agent}, x_Exit_door: {x_exit_door}, y_Exit_door: {y_exit_door}]"
    return s
