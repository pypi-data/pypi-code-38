import time
from threading import Thread, Event


class Timer(Thread):
    """A Timer repeats an action until stopped. The action is passed in and
        starts on a separate thread on every invocation. This is to prevent the duration
        of the action from interfering with the timing.
    """
    def __init__(self, delay, action=None):
        Thread.__init__(self)
        self.delay = delay
        self.stop_flag = Event()
        self.callback = action
        
    def run(self):
        while not self.stop_flag.wait(self.delay):
            if self.callback is not None:
                self.fire()
        
    def stop(self):
        self.stop_flag.set()

    def fire(self):
        thread = Thread(target=self.callback)
        thread.start()


if __name__ == '__main__':
    # Sample program
    def sayHi():
        print('hi')

    # Create a timer that executes something every second
    timer = Timer(1, sayHi)
    timer.start()
    
    # Main thread sleep for 3 seconds so the timer can execute a few times
    time.sleep(3)
    
    # Stop the timer
    timer.stop()
    
    # Wait for the timer to end along with this thread.
    timer.join()