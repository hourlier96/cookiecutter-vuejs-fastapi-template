# {{cookiecutter.project_name}}

{{ '=' * cookiecutter.project_name|length }}

## Description

{{cookiecutter.description}}

## Template Stack

- [FastApi](https://fastapi.tiangolo.com/)

## Project Setup

- Install [Poetry](https://python-poetry.org/docs/)

- Set config for venv in local

    ```bash
    poetry config virtualenvs.in-project true
    poetry install
    ```

### Run locally

```sh
# WITHOUT DOCKER (Guess ADC from env)
poetry shell                  # Launch terminal with dependencies
uvicorn app.main:app --reload # Or from VSCode launcher

# OR 

# WITH DOCKER
Use the launch.json configuration to build and run the container

# Hot reload
docker build -t <image>:<tag> -f Dockerfile .

# Export gcloud credentials & project

docker run --name {{ cookiecutter.project_slug }} -p 8000:8000 -p 5678:5678 -v "$HOME/.config/gcloud/application_default_credentials.json":/gcp/creds.json --env GOOGLE_APPLICATION_CREDENTIALS=/gcp/creds.json --env GCLOUD_PROJECT=<gcp_project_id> <image>:<tag>


```

## Api docs

- [Swagger](http://localhost:8000/docs)

### Maintainers

Digital Lab
