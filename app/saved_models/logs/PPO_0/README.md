# Tensorboard Logs
Para ver los logs creados por tensorboard de los entrenamientos que se fueron guardando

# Dependencia Numpy
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
