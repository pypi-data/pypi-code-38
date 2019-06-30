import click
from ain.workerMgr import Worker

@click.group()
@click.option('--type/--no-type', default=False)
def call(type):
    pass

@call.command()
@click.argument("command", type=click.Choice(['run', 'terminate', 'status', 'log', 'init']))
@click.option('--name', default="", help="ain worker name")
@click.option('--limit-count', default="", help="Maximum number of instances")
@click.option('--price', default="")
@click.option('--mnemonic', default="")
@click.option('--description', default="empty")
@click.option('--server-ip', default="empty")
def worker(command, name, limit_count, price, mnemonic, description, server_ip):
    
    optionRun = {
      'NAME': name,
      'LIMIT_COUNT': limit_count,
      'MNEMONIC': mnemonic,
      'PRICE': price,
      'DESCRIPTION': description,
      'SERVER_IP': server_ip
    }
    w = Worker()  
    if (command == "run"):
      w.run(optionRun)
    elif (command == "terminate"):
      w.terminate()
    elif (command == "status"):
      w.status()
    elif (command == "log"):
      w.log()
    elif (command == "init"):
      w.init()

    
if __name__ == '__main__':
    call()
