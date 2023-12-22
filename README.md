# cookie-cutter-vuejs-fastapi-template

VueJs & FastApi Stack template based on [cookiecutter](https://www.cookiecutter.io/)

## Installation

Install dependencies

```bash
cd cookiecutter-vuejs-fastapi-template
python3 -m pip install -r requirements.txt
```

## Usage

### Workspace

To open the template in VSCode, use the following command

```bash
cd cookiecutter-vuejs-fastapi-template
code .vscode/cookiecutter.code-workspace
```

### Generate Frontend Project

Use this repository to generate a Vuejs template project

```bash
cookiecutter cookiecutter-vuejs-fastapi-template/frontend   # Will ask your needs from cookiecutter.json
```

- **'repository_name'** allows you to specify an empty-existing Git repository.

```bash
<github_username>/<repo_name>  # Required format
```

If specified, it will auto-commit the generated template both in develop, uat & main branches.
Ensure you have corrects  **SSH rights & access**

- **'project_name'** is the name on the top of ReadMe.

- **'project_slug'** is the name of the generated folder

- **'description'** will be added under the project name in the ReadMe.

- **'maintainer'** has an informativ goal (not used in the template)

- **'navbar'** integrate a navbar with i18n support, and a dark mode switch.

- **'sidebar'** integrate a left sidebar with navigation.

- **'footer'** integrate a footer.

- **'as_container'** allow you to dockerize local run and auto deploy on Cloud Run

### Generate Backend Project (WIP)

Use this repository to generate a FastApi template project

```bash
cookiecutter cookiecutter-vuejs-fastapi-template/backend   # Will ask your needs from cookiecutter.json
```

- **'project_name'** is the name on the top of ReadMe.

- **'project_slug'** is the name of the generated folder

- **'description'** will be added under the project name in the ReadMe.

- **'maintainer'** has an informativ goal (not used in the template)

### TODO

#### Both

- Add access token to .env & check existence after project creation to call Github API

#### Back

- Allow to choose either Firestore or SQL + use multi cookiecutter.json
- CookieCut Dockerfile questions & Cloud Run deploy
