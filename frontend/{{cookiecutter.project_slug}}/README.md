# {{cookiecutter.project_name}}

{{ '=' * cookiecutter.project_name|length }}

## Description

{{cookiecutter.description}}

## Template Stack

- [Vue3 with Composition API](https://vuejs.org/guide/introduction.html)
- [Vuetify](https://vuetifyjs.com/en/getting-started/installation/)
- [Pinia](https://pinia.vuejs.org/)
- [piniaPluginPersistedstate](https://github.com/prazdevs/pinia-plugin-persistedstate/)

## Formatting / Linting

The template is using [ESLint for VueJS](https://eslint.vuejs.org/).

By default, **auto formatting is enabled on save**.

## I18N

To add any new langage:

- Add new languages in JSON format to `i18n` directory
- Complete 'languages' & 'countries_info' variables in `i18n/index.js`

(see [vue-i18n](https://kazupon.github.io/vue-i18n/) for more documentation)

(see [vue-country-flag-next](https://www.npmjs.com/package/vue-country-flag-next) for country flags)

## Project Setup

### Run locally

```sh
# WITHOUT DOCKER
npm install
npm run dev

# OR 

# WITH DOCKER
# Dev server (vite)
docker build -t <image>:<tag> -f Dockerfile.dev .
docker run --name {{ cookiecutter.project_slug }} -p 5173:5173 <image>:<tag>

# Prod server (nginx)
docker build -t <image>:<tag> -f Dockerfile.prod .
docker run --name {{ cookiecutter.project_slug }} -p <host_port>:8080 <image>:<tag>  # Port forward to nginx

```

## CI/CD

### CI with Github Actions

Use .github/workflows/lint.yaml by enabling Github Actions API in your repository

This will run linting for every Pull Request on develop, uat and master branches

### CD with Cloud Build & Cloud Run

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

### Maintainers

{{cookiecutter.maintainer}}
