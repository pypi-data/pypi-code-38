import os
import shutil
import subprocess
import sys
import time


def create_n_upload():
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    some_command = (
        sys.executable + " " + os.path.basename(__file__) + " sdist bdist_wheel"
    )
    p = subprocess.Popen(some_command, stdout=subprocess.PIPE)
    while True:
        output = p.stdout.readline().decode("utf-8")
        if output == "" and p.poll() is not None:
            break
        if output:
            print(output.strip())
        time.sleep(0.01)
    rc = p.poll()
    some_command = sys.executable + " -m twine upload dist/*"
    p = subprocess.Popen(some_command, stdout=subprocess.PIPE)
    while True:
        output = p.stdout.readline().decode("utf-8")
        if output == "" and p.poll() is not None:
            break
        if output:
            print(output.strip())
        time.sleep(0.01)
    rc = p.poll()


if __name__ == "__main__":
    shutil.rmtree(os.path.join(os.path.dirname(os.path.abspath(__file__)),"dist"), ignore_errors=True)
    shutil.rmtree(os.path.join(os.path.dirname(os.path.abspath(__file__)),"build"), ignore_errors=True)
    if len(sys.argv) == 1:
        create_n_upload()
    else:
        import setuptools
        from setup import setup

        setup = setup
        setup["version"] = setup["version"] + "." + str(int(time.time()))
        print(setup["version"])
        setuptools.setup(**setup)
