from setuptools import setup, find_packages

def main():
    setup(
        name = "test-pip-install",
        version = "0.0.3",
        packages = find_packages(),
        author = "Valentin Niess",
        author_email = "valentin.niess@gmail.com",
        description = "Test if `pip install` is working",
        long_description = open("README.md").read(),
        long_description_content_type = "text/markdown",
        url = "https://github.com/niess/test-pip-install",
        classifiers = [
            "Programming Language :: Python",
            "Development Status :: 4 - Beta",
            "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
            "Natural Language :: English",
            "Operating System :: OS Independent",
            "Topic :: Software Development :: Testing"
        ],
        entry_points = {
            "console_scripts" : ("test-pip-install=test_pip_install:info",)
        }
    )

if __name__ == "__main__":
    main()
