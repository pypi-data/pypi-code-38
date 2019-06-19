import threading

class GlobalManager():

    def __init__(self):
        self.experiments = {}
        self.callers = {}
        self.lock = threading.Lock()


    def add(self,experiment,caller_filename):
        try:
            self.lock.acquire()
            self.experiments[experiment.name] = experiment
            self.callers[caller_filename] = experiment.name
        except:
            self.lock.release()

    def remove(self,experiment_name):
        try:
            self.lock.acquire()
            self.experiments.pop(experiment.name)
            for key in self.callers:
                if self.callers[key] == experiment_name:
                    self.callers.pop(key)
                    break
        except:
            self.lock.release()


global_manager = GlobalManager()