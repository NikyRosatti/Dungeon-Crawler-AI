# Tensorboard Logs
Para ver los logs creados por tensorboard de los entrenamientos que se fueron guardando

Modificar en el código en la parte de la creación del modelo (PPO por ejemplo) tal que:

<i>model = PPO("MlpPolicy", env=envs, ...<b>tensorboard_log=logdir</b>)</i>


# Dependencia Numpy y TensorFlow

## Ubuntu
Para poder ver los logs correctamente, la version de Numpy tiene que ser numpy<2.0.0

Se deberia reemplazar y desinstalar
``` txt
numpy==2.1.1
```
Del <b>requirements.txt</b>
Por
```txt
numpy<2.0.0
```

Y hacer el comando
``` bash
pip install -r requirements.txt
```

# Instalar TensorFlow
Se necesita TensorFlow instalado para poder ver Tensorboard

## Instalacion global
Instalar globalmente TensorFlow

``` bash
pip install TensorFlow
```

## Instalacion local
En <b>requirements.txt</b> se encuentra Tensorflow como dependencia de Pip
Al hacer
``` bash
pip install -r requirements.txt
```
Se deberia instalar tambien sin problemas

# Ver Logs
Pararse una carpeta antes de logs/

Por ejemplo:
``` bash
cd /app/saved_models
```

Hacer:

``` bash
tensorboard --logdir=logs
```
