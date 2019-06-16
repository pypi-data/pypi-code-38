from .run import run
from . import context
run.Context = context.Context
run.Quash = context.Quash
run.Enforce = context.Enforce
run.Cwd = context.Cwd
run.Stdio = context.Stdio
run.Log = context.Log
run.Sudo = context.Sudo
run.New = context.New
del context
