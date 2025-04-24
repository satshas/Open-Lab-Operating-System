# Open-Lab-Operating-System Server

The server for the open lab operation system that connect to the machine

## Install the dependencies

1- create a virtual environment:

```bash
python -m venv venv
```

2- activate the virtual environment

```bash
# windows
venv/Scripts/activate

# linux / macos
source venv/bin/activate
```

3- install dependencies

```bash
pip install -r requirements.txt
```

### Start the server

After activating the virtual environment run the following command:

```bash
python src/main.py
```

## Customize the configuration

Please modify the configuration of the machine in the `config.yaml` file before starting the server.

## AI Image generating usage
If you would like to AI image generator, please create a folder in the main directory `AI_models` and install the model that you need, and put it inside the created folder.

P.S. You can find supported models in the `config.yaml` file
