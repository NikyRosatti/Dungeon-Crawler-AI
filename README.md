# Dungeon Crawler AI
Subject <i>Proyecto.</i>

<i>Universidad Nacional de Río Cuarto, Córdoba, Argentina.</i>

In this repo we built a gym environment to train an AI by using Reinforcement Learning.

Is a web application that lets you build a maze, where an agent have to learn how to escape from there by dodging some obstacles.

# Prerequisites
We created this app by using Python, so its an obvious must-have!

## Installation
Make sure you have Python 3.8 or higher installed on your machine. You can verify your Python version by running the following command:

```bash
python --version
```

You also need pip, which is Python's package installer. If you don't have it installed, follow the instructions below:

### Installing pip
On Linux / WSL.
```bash
sudo apt install python3-pip
```

### Setting Up a Virtual Environment
It is recommended to use a virtual environment to manage dependencies. To create and activate a virtual environment, use the following commands:

#### Debian / Ubuntu / WSL
On Debian/Ubuntu systems, you need to install the python3-venv package using the following command.
```bash
sudo apt install python3.10-venv
```

#### Create virtual environment
```bash
python -m venv venv
```

#### Activate the virtual environment
Activate the virtual environment on <b>Linux or macOS</b> by doing:
```bash
source venv/bin/activate
```

Activate the virtual environment on <b>Windows</b> by doing:
```shell
.\venv\Scripts\activate
```

### Installing Dependances
Once the virtual environment is activated, install the required dependencies listed in requirements.txt:
```bash
pip install -r requirements.txt
```

On <b>Windows</b>:
```shell
pip install -r .\requirements.txt
```

# Usage
Once everything is set properly...

### Running the app
``` python
python3 run.py
```

### Localhost:
```
http://127.0.0.1:5000
```

## Tests
To run the tests provided in the project

Install the requeriments.txt dependances and run:
```
pytest
```
