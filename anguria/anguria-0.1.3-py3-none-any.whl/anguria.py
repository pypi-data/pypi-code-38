#!/usr/bin/env python

class AnguriaScanner:

    def __init__(self):
        self.mode = "dummy"
        pass

    def __init__(self, filename):
        self.mode = "SingleFile"
        pass

    def __init__(self, filenames):
        self.mode = "MultipleFiles"
        pass

    def get_mode(self):
        return self.mode
