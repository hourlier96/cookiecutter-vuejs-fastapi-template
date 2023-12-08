import os

# Add root to path, so hooks_modules can be imported from the
# temporary directory created by cookiecutter while generating
# This allows to split the code in multiple files
# https://github.com/cookiecutter/cookiecutter/issues/1593
import sys

PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)
sys.path.insert(0, PROJECT_DIRECTORY)

from hooks_modules import main


if __name__ == "__main__":
    print("\nRunning post generation hooks...\n")
    try:
        if "{{ cookiecutter.repository_name}}":
            print("Pushing template to {{ cookiecutter.repository_name }}...")
            main.checkRepositoryNameOption("{{ cookiecutter.repository_name }}")

        if "{{ cookiecutter.as_container }}" == "False":
            main.checkAsContainerOption()

        print("\nDone ! 🎉")
        print(
            "Project is ready to be used in folder './{{ cookiecutter.project_slug }}'"
        )
        print("Check the README.md for more information about how to use the project")
    except Exception as e:
        print(e)
        sys.exit(1)
