import functools
from threading import Event, Thread
from ioflow.proto_task_manager import task_manager


def fake_client(event):
    import time
    i = 0
    while i < 30:
        i += 1
        event.wait()
        time.sleep(1)
        print("I am working pre 1s")


event = Event()
event.set()

app = task_manager(event)


threads = []
# for func in [functools.partial(fake_client, event), app.run]:
for func in [app.run]:
    t = Thread(target=func)
    t.setDaemon(True)
    t.start()
    threads.append(t)

fake_client(event)

# for thread in threads:
#    """
#    Waits for threads to complete before moving on with the main
#    script.
#    """
#    thread.join()


