import json
import os
import time

from flask import session

from app.environment.maze import Maze, N_MAX_STEPS
from app.models import User, MazeBd, db
from app.services.map_services import action_to_string

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

running_tests = {}


def train_model(maze_id):

    maze = MazeBd.query.filter_by(id=maze_id).first()

    grid1 = json.loads(maze.grid)
    size = maze.maze_size

    grid = [grid1[i : i + size] for i in range(0, len(grid1), size)]

    log_dir = os.path.join("app", "saved_models", "logs", f"{maze_id}")
    os.makedirs(log_dir, exist_ok=True)

    num_envs = 5
    env = DummyVecEnv([lambda: Maze(grid) for _ in range(num_envs)])

    model_path = f"app/saved_models/trained_models_per_id/{maze_id}/"
    os.makedirs(model_path, exist_ok=True)

    try:
        env = VecNormalize.load(load_path=model_path + "norm_env.pkl", venv=env)
        print("TrainEnv: Retraining the environment")
    except:
        env = VecNormalize(env, norm_obs=False, norm_reward=True, clip_obs=10.0)
        print("TrainEnv: Creating the environment")

    try:
        model = PPO.load(path=model_path + "ppo.zip", env=env)
        print("TrainModel: Retraining the model")
    except:
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

    results = {"status": "running", "map": None}

    print(f"Minimum steps required to solve the maze: {env.envs[0].minimum_steps}")

    user = User.query.get(session["user_id"])
    env.training = False
    env.norm_reward = False
    obs = env.reset()
    steps = 0
    while steps < N_MAX_STEPS:
        steps += 1
        print(f"Steps: {steps}")

        if not running_tests.get(maze_id):  # Si se ha solicitado detener la prueba
            print(f"Test stopped for maze_id {maze_id}")
            results["status"] = "stopped"
            yield results
            running_tests.pop(maze_id, None)
            break

        action, _ = model.predict(obs)
        print(f"  Action according to the prediction: {action_to_string(action)}")
        obs, reward, done, _ = env.step(action)
        print(
            f"  Observation after the step: {obs_to_string(obs)}"
            + f"  Reward: {reward}, Done: {done}"
        )

        current_map_state = env.envs[0].get_current_map_state()
        results["map"] = current_map_state
        yield results
        time.sleep(0.05)

        if done:
            print("Maze solved")
            if user:
                if maze not in user.completed_dungeons:
                    user.completed_dungeons.append(maze)
                    if env.envs[0].minimum_steps == steps:
                        user.points += size + steps
                    else:
                        user.points += size
                    db.session.commit()
                    results["status"] = "finished"
                    yield results
                    print(f"User {user.username} completed the maze {maze_id}.")
                else:
                    print(f"The user {user.username} already completed this maze.")
            results["status"] = "finished"
            yield results
            break

        if env.envs[0].lose:
            print(f"Your agent could not complete the maze in {N_MAX_STEPS} steps!!")

    running_tests.pop(maze_id, None)  # Eliminar la prueba de la lista de ejecuciones


def setup_environment(grid, maze_id):
    """Configura el entorno de entrenamiento y carga el modelo PPO."""
    vec_norm_path = f"app/saved_models/trained_models_per_id/{maze_id}/norm_env.pkl"
    env = DummyVecEnv([lambda: Maze(grid)])
    try:
        env = VecNormalize.load(load_path=vec_norm_path, venv=env)
        print(f"Loading the environment {vec_norm_path}")
    except:
        print(f"Vectorized environment not found, loading a generic one")
        env = VecNormalize(env, norm_obs=False, norm_reward=True, clip_obs=10.0)

    try:
        model_to_load = f"app/saved_models/trained_models_per_id/{maze_id}/ppo.zip"
        model = PPO.load(model_to_load, env=env)
        print(f"Loading the file {model_to_load}")
    except:
        model = PPO("MlpPolicy", env=env)
        print("Playing without a trained model!")

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
    x_Agent = obs[0]
    y_Agent = obs[1]
    x_Exit_door = obs[2]
    y_Exit_door = obs[3]
    s = f"[X_Agent: {x_Agent}, Y_Agent: {y_Agent}, x_Exit_door: {x_Exit_door}, y_Exit_door: {y_Exit_door}]"
    return s
