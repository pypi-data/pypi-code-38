"""Async wrapper around Inotify to provide event-iterable"""
from __future__ import absolute_import
from fussy import inotify
import asyncio

async def iter_events(watch):
    queue = asyncio.Queue()
    async def push_to_queue():
        for event in inotify.get_events_nonblocking(watch):
            event.fd = watch
            event.wd = watch.watches.get(event.wd,event.wd)
            await queue.put(event)

    def on_readable():
        asyncio.ensure_future(push_to_queue())
    reader = asyncio.get_event_loop().add_reader(int(watch), on_readable)

    event = True
    while not watch.closed:
        event = await queue.get()
        if event is None:
            break
        yield event 

def main():
    import sys
    target = sys.argv[1]
    watch = inotify.Inotify()
    watch.add_watch(target)
    async def demo():
        print("Touch or otherwise modify first argument to produce 5 events")
        count = 0
        async for event in iter_events(watch):
            print("Event", event)
            count += 1
            if count > 4:
                break 

    asyncio.get_event_loop().run_until_complete(demo())

if __name__ == "__main__":
    main()
