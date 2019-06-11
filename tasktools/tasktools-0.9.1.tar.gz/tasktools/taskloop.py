import asyncio
import functools

#every coroutine
async def coromask(coro, args, fargs):
    """
    A coroutine that mask another coroutine  callback with args, and a
    function callbacks who manage input/output of corotine callback

    :param coro: is a coroutine object defined by the developer
    :param args: the list of arguments to run on the corotine *coro*
    :param fargs: the function that process the input and create an output related with the coro result

    :returns: a result, is a list of the elements for future argument
    """
    try:
        _in = args
        msg = ("Coromask args %s in coro %s" %(args, coro) )
        obtained = await coro(*args)
        if isinstance(obtained, Exception):
            raise Exception()
        else:
            result = fargs(_in, obtained)
            return result
    except Exception:
        print(msg)
        raise Exception
   
def renew(task, coro, fargs, *args):
    """
    A simple function who manages the scheduled task and set the
    renew of the task

    :param task: is a Future initialized coroutine but not executed yet
    :param coro: is the corutine to renew when the first is finished
    :param fargs: the function to process input/output
    :param args: the unpacked list of extra arguments
    """
    if task.exception():
        print("Excepcion")
        raise task.result()
    else:
        result = task.result()
        loop = asyncio.get_event_loop()
        task = loop.create_task(coromask(coro, result, fargs))
        task.add_done_callback(functools.partial(renew, task, coro, fargs))

   
def renew_quamash(task, coro, fargs, loop, *args):
    """
    A simple function who manages the scheduled task and set the
    renew of the task.
    The same as *renew* but it can be used with different *event loop* like *quamash* for *qt*

    :param task: is a Future initialized coroutine but not executed yet
    :param coro: is the corutine to renew when the first is finished
    :param fargs: the function to process input/output
    :param loop: a different event loop from *asyncio*
    :param args: the unpacked list of extra arguments

    """
    if task.exception():
        print("Excepcion")
        raise task.result()
    else:
        result=task.result()
        task=loop.create_task(coromask(coro, result, fargs))
        task.add_done_callback(functools.partial(renew_quamash, task, coro, fargs,loop))

def simple_fargs(_in, obtained):
    """
    Simple function who can be used in callback on coromask, the
    inputs are /_in/ and /obtained/ value from the coroutine executed.
    Return _in

    :_in: the input list
    :param obtained: the object that came from the result of coroutine execution

    :returns: _in
    """
    return _in


def simple_fargs_out(_in, obtained):
    """
    Simple function who can be used in callback on coromask, the
    inputs are /_in/ and /obtained/ value from the coroutine executed.
    Return obtained

    :param _in: the input list
    :param obtained: the object that came from the result of coroutine execution

    :returns: obtained
    """
    return obtained
