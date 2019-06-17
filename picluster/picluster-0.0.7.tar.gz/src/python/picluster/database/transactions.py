# from dxl.picluster.database.model import Task, taskSchema
# from functools import singledispatch
#
#
# @singledispatch
# def serialization(t):
#     raise NotImplemented
#
#
# @serialization.register(Task)
# def _(t):
#     return taskSchema.dump(t)
#
#
# def deserialization(t):
#     if t == "starts":
#         pass
#
#     elif set(t.keys()).issubset(set(taskSchema.declared_fields.keys())):
#         return Task(**taskSchema.load(t))
