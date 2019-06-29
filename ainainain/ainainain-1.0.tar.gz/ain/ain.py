import click
from ain.workerMgr import Worker

@click.group()
@click.option('--type/--no-type', default=False)
def call(type):
    pass

@call.command()
@click.argument("command", type=click.Choice(['run', 'terminate', 'status', 'log']))
def worker(command):
    w = Worker()  
    if (command == "run"):
        w.run()
    elif (command == "terminate"):
        w.terminate()
    elif (command == "status"):
        w.status()
    elif (command == "log"):
        w.log()

    
if __name__ == '__main__':
    call()
