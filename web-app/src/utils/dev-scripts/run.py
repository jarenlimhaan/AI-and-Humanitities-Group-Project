from subprocess import run

def dev():
    run(["poetry", "run", "python", "main.py"])