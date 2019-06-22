from invoke import task, Collection
from magicinvoke import magictask, Lazy

ns = Collection()

@ns.magictask(no_ctx=True)
def mine(ctx):#, output_path=Lazy('ctx.output_pathlol')):
    print(ctx)
    print(output_path + '')
    pass

@task(mine)
def mytask(ctx):
    pass

@ns.task(no_ctx=True)
def noctxtask():
    print("hi")
    return

# Used to test error msgs
ns.configure({"tasks": {"mine": {"output_path1": lambda ctx: "/dev/null"}}})
#ns.configure({"tasks": {"mine": lambda ctx: 2+{"output_path": lambda ctx: "/dev/null"}}})
