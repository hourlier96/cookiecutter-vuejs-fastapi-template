# {{cookiecutter.project_name}}

{{ '=' * cookiecutter.project_name|length }}

## Description

{{cookiecutter.description}}

## Template Stack

- [FastApi](https://fastapi.tiangolo.com/)
- [SQLModel](https://sqlmodel.tiangolo.com/)
- [SQLAlchemy 2](https://docs.sqlalchemy.org/en/20/)

## Project Setup

- Install [Poetry](https://python-poetry.org/docs/)

- Set config for venv in local

  ```sh
  poetry config virtualenvs.in-project true
  poetry env use 3.11
  poetry shell
  poetry install
  ```

- Create required databases

  ```bash
  docker compose up -d
  ```

- Apply migrations

  ```sh
  alembic upgrade head        # Ensure your database is running, and SQLALCHEMY_DATABASE_URI env variable is correctly setup
  ```

### Run locally

```sh
# WITHOUT DOCKER (Guess ADC from env)
uvicorn app.main:app --reload          # Or from VSCode launcher

# OR

# WITH DOCKER
Use the launch.json configuration to build and run the container

# (Running the launch is an equivalent to):
docker build -t <image>:<tag> -f Dockerfile .
docker run --name {{ cookiecutter.project_slug }} -p 8000:8000 -p 5678:5678 -v "$HOME/.config/gcloud/application_default_credentials.json":/gcp/creds.json --env GOOGLE_APPLICATION_CREDENTIALS=/gcp/creds.json --env GCLOUD_PROJECT=<gcp_project_id> <image>:<tag>

```

## Tests

```sh
poetry run pytest --cov=app --cov-report=term     # Uses SQLALCHEMY_DATABASE_URI in pyproject.toml
```

### Deployment

.cloudbuild/cloudbuild.yaml is used automatically to deploy to Cloud Run according to your Cloud Build trigger configuration

*Requirements*:

- Create a Cloud Build trigger and specify the cloudbuild.yaml path
  - You will have to link Github repository to Cloud Build

- Add .env in a Secret named '{{ cookiecutter.project_slug.replace('_', '-') }}'

- APIs enabled:

  - Cloud Build API
  - Cloud Run API
  - Secret Manager API

- Roles:

  - Cloud Build Service Account has Cloud Run Admin role
  - Cloud Build Service Account has Secret Manager Secret Accessor role

### Cloud Run & Cloud SQL

To allow communication between Cloud Run service & SQL instance:

- Make sure connection string in .env is correct
- [Add the connection name of your SQL instance in Cloud Run service configuration](https://cloud.google.com/sql/docs/postgres/connect-run#configure)

## Api docs

- [Swagger](http://localhost:8000/api/docs)

### Maintainers

{{cookiecutter.maintainer}}
