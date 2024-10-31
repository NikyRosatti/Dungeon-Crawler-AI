from app.environment.maze import Maze
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
import torch.nn as nn
import numpy as np
import os


def suggest_architecture(trial):
    arch_str = trial.suggest_categorical("net_arch", ["64_64", "128_128", "256_256"])
    if arch_str == "64_64":
        return [64, 64]
    elif arch_str == "128_128":
        return [128, 128]
    elif arch_str == "256_256":
        return [256, 256]


def suggest_activation_fn(trial):
    activation_str = trial.suggest_categorical(
        "activation_fn", ["ReLU", "Tanh"]
    )  # Usa strings
    if activation_str == "ReLU":
        return nn.ReLU
    elif activation_str == "Tanh":
        return nn.Tanh


def optimize_ppo(trial, grid):
    # Definir los hiperparámetros que Optuna va a optimizar
    learning_rate = trial.suggest_float("learning_rate", 1e-5, 1e-2)
    gamma = trial.suggest_float("gamma", 0.8, 0.9999)
    gae_lambda = trial.suggest_float("gae_lambda", 0.8, 1.0)
    ent_coef = trial.suggest_float("ent_coef", 1e-8, 0.1)
    vf_coef = trial.suggest_float("vf_coef", 0.1, 1.0)

    net_arch = suggest_architecture(trial)
    activation_fn = suggest_activation_fn(trial)
    ortho_init = trial.suggest_categorical("ortho_init", [True, False])

    policy_kwargs = dict(
        net_arch=net_arch,
        activation_fn=activation_fn,
        ortho_init=ortho_init,
    )

    vec_norm_path = os.path.join("app", "saved_models", "vec_normalize.pkl")
    if os.path.exists(vec_norm_path):
        os.remove(vec_norm_path)
        print(
            f"Model: Archivo existente {vec_norm_path} eliminado para crear uno nuevo"
        )

    model_path = os.path.join("app", "saved_models", "ppo_dungeons.zip")
    if os.path.exists(model_path):
        os.remove(model_path)
        print(f"Model: Archivo existente {model_path} eliminado para crear uno nuevo")

    logdir = os.path.join("app", "saved_models", "logs")
    if not os.path.exists(logdir):
        os.makedirs(logdir)
    # Crear los entornos
    envs = make_env(grid)
    print("Vec: Creando el archivo de normalización")

    # Definir el modelo PPO con los hiperparámetros seleccionados
    model = PPO(
        "MlpPolicy",
        env=envs,
        learning_rate=learning_rate,
        n_steps=2048,
        batch_size=64,
        gamma=gamma,
        gae_lambda=gae_lambda,
        ent_coef=ent_coef,
        vf_coef=vf_coef,
        clip_range=0.2,
        policy_kwargs=policy_kwargs,
        verbose=0,
        tensorboard_log=logdir
    )
    print("Model: Creando el modelo")

    print("Inicio entrenamiento")
    model.learn(total_timesteps=20000, progress_bar=True)
    print("Fin entrenamiento")

    # Evaluar el modelo (puedes adaptar esta parte según cómo mides el rendimiento)
    print("Inicio evaluacion del modelo")
    mean_reward = evaluate_model(model, envs)
    print("Fin evaluacion del modelo")

    # Guardar el modelo y la normalizacion después de la optimizacion
    model_path = os.path.join("app", "saved_models", "ppo_dungeons.zip")
    model.save(model_path)
    print("Modelo guardado con éxito")
    envs.save(vec_norm_path)
    print("Entornos guardados con éxito")

    return float(mean_reward)


def evaluate_model(model, envs):
    rewards = []
    obs = envs.reset()
    total_reward = 0
    n_steps = 0
    total_steps = 400
    env_done = False
    while n_steps < total_steps and not env_done:
        action, _ = model.predict(obs)
        obs, reward, done, _ = envs.step(action)
        total_reward += reward
        rewards.append(total_reward)
        if done.any():
            env_done = True
        n_steps += 1
    return np.mean(rewards)


def make_env(grid):
    env = Maze(grid)
    return env
