from setuptools import setup, find_packages

setup(
    name = "convokit",
    author = "Cristian Danescu-Niculescu-Mizil, Andrew Wang",
    author_email = "azw7@cornell.edu",
    url = "https://github.com/CornellNLP/Cornell-Conversational-Analysis-Toolkit",
    description = "Cornell Conversational Analysis Toolkit",
    version = "2.0.4",
    packages = ["convokit", "convokit.politeness_api",
        "convokit.politeness_api.features"],
    package_data = {"convokit": ["data/*.txt"]},
    entry_points = {
        "console_scripts": ["convokit = convokit.command_line:command_line_main"]
    },
    install_requires = [
        "matplotlib>=3.0.0",
        "pandas>=0.23.4",
        "spacy==2.0.12",
        "scipy>=1.1.0",
        "scikit-learn>=0.20.0",
        "nltk>=3.4",
        "dill>=0.2.9"
    ]
)
