# Aida - Rasa X Demo Bot

The chatbot is setup to run under the lighterweight local Rasa X install in a Docker container with `docker-compose`.

Update the version numbers in the `.env` file. You can find the version info in the tags for the [Docker Hub Images](https://hub.docker.com/u/rasa).

```
RASA_X_VERSION=0.26.0
RASA_VERSION=1.8.1
RASA_SDK_VERSION=1.7.0
```

You can run your own copy of the bot using these steps:

```sh
git clone https://github.com/statecs/aida.git
cd aida
sudo docker-compose build --no-cache
sudo docker-compose run rasa-x rasa train
sudo docker-compose up -d
sudo docker-compose logs rasa-x | grep password
```

## Ports

The `docker-compose.yml` uses the default ports which can be over-ridden. This is partcularly useful if you want to run multiple chatbots on the same host.

- `5005` - Rasa port (point your client here) (Also uses `80` and `443`)
- `5002` - Rasa X UI

# Update Server

To update the server, update the version numbers in the `.env` and enter the following commands

```sh
sudo docker-compose down
sudo docker-compose up -d
sudo docker-compose logs rasa-x | grep password
```

# Training

Local training using your local python environment (or conda/venv)

```sh
docker-compose run rasa-x rasa train
```

# Testing

After training the model, run the command:

```sh
docker-compose run rasa-x rasa test nlu -u test/test_data.md --model models/$(ls models)
docker-compose run rasa-x rasa test core --stories test/test_stories.md
```

# Rasa Interactive Shell


With Docker:

```sh
docker run -it -v $(pwd):/app rasa/rasa:1.8.1 run actions --actions actions.actions
docker-compose up app
docker run -it -v $(pwd):/app rasa/rasa:1.8.1 shell --debug --endpoints endpoints_local.yml
```

Starts an interactive learning session to create new training data by chatting.
https://rasa.com/docs/rasa/user-guide/command-line-interface/

```sh
docker run -it -v $(pwd):/app rasa/rasa:1.8.1 interactive --debug --endpoints endpoints_local.yml
```

# Scripts

The project includes the following scripts:

| Script              | Usage                              |
| ------------------- | ---------------------------------- |
| entrypoint.sh       | Docker entrypoint for full Rasa X  |
| entrypoint_local.sh | Docker entrypoint for local Rasa X |

# Rasa X & Rasa Version Combinations

| Rasa X |  Rasa  | Rasa SDK |
| :----: | :----: | :------: |
| 0.25.1 | 1.7.0  |  1.7.0   |
| 0.24.6 | 1.6.1  |  1.6.1   |
| 0.23.5 | 1.5.3  |  1.5.2   |
| 0.23.3 | 1.5.1  |  1.5.0   |
| 0.22.1 | 1.4.3  |  1.4.0   |
| 0.21.5 | 1.3.9  |  1.3.3   |
| 0.21.4 | 1.3.9  |  1.3.3   |
| 0.21.3 | 1.3.9  |  1.3.3   |
| 0.20.5 | 1.2.11 |  1.2.0   |
| 0.20.0 | 1.2.5  |  1.2.0   |

## Training Times

| Rasa Version | Pipeline | Time |
|:---:|---|:---:|
| 1.8 | EmbeddingIntentClassifier | 1:07 |
| 1.8 | DIETClassifier | 2:10 |

## ToDo
- Use FormAction
- NLU test data
- Core test data
- Rasa validate
- Support [multi-intents](https://blog.rasa.com/how-to-handle-multiple-intents-per-input-using-rasa-nlu-tensorflow-pipeline/?_ga=2.50044902.1771157212.1575170721-2034915719.1563294018)
- Google Assistant integration

### Cred
https://github.com/rgstephens/jokebot



