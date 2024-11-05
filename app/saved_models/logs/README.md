# Tensorboard Logs
To view the logs created by TensorBoard from the training sessions that were saved,

Modify the code in the part where the model is created (for example, PPO) as follows:

<i>model = PPO("MlpPolicy", env=envs, ...<b>tensorboard_log=logdir</b>)</i>


# Dependencies: Numpy and TensorFlow

## Ubuntu
To properly view the logs, the version of Numpy must be numpy<2.0.0

You should replace and uninstall:
``` txt
numpy==2.1.1
```
In the <b>requirements.txt</b> file
with
```txt
numpy<2.0.0
```

Then, run the following command:
``` bash
pip install -r requirements.txt
```

# Install TensorFlow
TensorFlow is required to view TensorBoard

## Global Installation
To install TensorFlow globally, run:

``` bash
pip install TensorFlow
```

## Local Installation
If TensorFlow is listed as a dependency in <b>requirements.txt</b>, simply run:
``` bash
pip install -r requirements.txt
```
This should install it without any issues

# View Logs
Navigate one directory before the logs/ folder.

For example:
``` bash
cd /app/saved_models
```

Then, run the following command:

``` bash
tensorboard --logdir=logs
```
