import ataleek.github_hub as hub
import os
import yaml
import shutil

ARG_PARSER_CONFIG = {"prog": "Ataleek", "description": "Ataleek CLI"}
default_pr_message = """Solution

Please verify all aspects of this solution i.e Algorithm, Data Structures,
Modules, Design Patterns etc.

Review the code as finely as possible.
"""

def get_username():
    with open(os.path.expanduser("~/.config/hub"), 'r') as stream:
        try:
            config = yaml.safe_load(stream)
            username = config['github.com'][0]['user']
            return username
        except yaml.YAMLError as exc:
            print(exc)

def submit_solution(pr_message):
    answer = input("Have you completely implemented the solution? [y/n] ")
    if answer.lower() == "y":
        hub.pull_request(pr_message)
    else:
        print("Please implement the solution completely before submitting the solution.")

def get_project(repo_name):
    repo_dir_name = repo_name.split("/")[1]
    
    response = hub.clone(repo_name)
    if response.returncode == 0:
        os.chdir(repo_dir_name)
    hub.fork()
    os.chdir("..")
    shutil.rmtree(repo_dir_name, ignore_errors=True)
    hub.clone(f"{get_username()}/{repo_dir_name}")