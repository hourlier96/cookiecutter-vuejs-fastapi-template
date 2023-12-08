import os
import shutil
import git


def checkRepositoryNameOption(repo_name):
    """
    Check if repository_name is empty,
    if not init & fill empty git repo
    """
    repo_name = "{{ cookiecutter.repository_name }}"
    if not repo_name:
        return

    shutil.rmtree("hooks_modules")

    g = git.cmd.Git(repo_name)
    g.init()
    g.remote("add", "origin", f"git@github.com:{repo_name}.git")
    g.add(".")
    g.commit("-m", "Commit made by cookiecutter")
    g.branch("-M", "main")

    g.branch("develop")
    g.merge("develop")

    g.branch("uat")
    g.merge("uat")

    g.config("init.defaultBranch", "develop")

    g.push("-u", "origin", "--all")
    print(f"Pushed to remote repository: https://github.com/{repo_name}")


def checkAsContainerOption():
    """
    Check if as_container is empty,
    if not init & fill empty git repo
    """
    as_container = "{% if cookiecutter.as_container %}y{% endif %}"
    if not as_container:
        print("Removing docker requirements...")
        os.remove("Dockerfile.dev")
        os.remove("Dockerfile.prod")
        shutil.rmtree(".cloudbuild")
