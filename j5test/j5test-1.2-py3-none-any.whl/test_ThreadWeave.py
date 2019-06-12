#!/usr/bin/env python

import threading
import time
from j5test import ThreadWeave
from j5basic.WithContextSkip import StatementSkipped

class TestTheBoringWay(object):
    def eat_burgers(self, name):
        """eat burgers, one at a time, and add fries to the end when you do"""
        while True:
            with self.items_lock:
                if not self.items_to_eat:
                    break
                if self.items_to_eat[0] == "burger":
                    self.items_to_eat.pop(0)
                    self.sequence.append(name)
                    self.items_to_eat.append("fries")
            time.sleep(0.05)

    def eat_fries(self, name):
        """eat as many fries at once as you can"""
        while True:
            with self.items_lock:
                if not self.items_to_eat:
                    break
                if self.items_to_eat[0] == "fries":
                    self.sequence.append(name)
                while self.items_to_eat and self.items_to_eat[0] == "fries":
                    self.items_to_eat.pop(0)
            time.sleep(0.05)

    def test_each_complete(self):
        self.items_lock = threading.Lock()
        self.items_to_eat = ["fries", "burger", "fries", "burger"]
        self.sequence = []
        self.burger_eater = threading.Thread(target=self.eat_burgers, args=("ryan",), name="eat_burgers")
        self.fries_eater = threading.Thread(target=self.eat_fries, args=("sophie",), name="eat_fries")
        self.burger_eater.start()
        self.fries_eater.start()
        self.burger_eater.join()
        self.fries_eater.join()
        assert self.sequence == ["sophie", "ryan", "sophie", "ryan", "sophie"]

class TestNonBlockingWeave(object):
    """This is a simple test of the same concept being done in a single method, without artificial blocking"""
    def eatery(self, name):
        """A method that can be entered by multiple threads, and decides what to do as it processes the queue depending on which thread is active"""
        while True:
            with self.items_lock:
                if not self.items_to_eat:
                    break
                with ThreadWeave.only_thread('eat_burgers') as StatementSkipped.detector:
                    # eat burgers, one at a time, and add fries to the end when you do
                    if self.items_to_eat[0] == "burger":
                        self.items_to_eat.pop(0)
                        self.sequence.append(name)
                        self.items_to_eat.append("fries")
                with ThreadWeave.only_thread('eat_fries') as StatementSkipped.detector:
                    # eat as many fries at once as you can
                    if self.items_to_eat[0] == "fries":
                        self.sequence.append(name)
                    while self.items_to_eat and self.items_to_eat[0] == "fries":
                        self.items_to_eat.pop(0)
            time.sleep(0.05)

    def test_each_complete(self):
        self.items_lock = threading.Lock()
        self.items_to_eat = ["fries", "burger", "fries", "burger"]
        self.sequence = []
        self.burger_eater = threading.Thread(target=self.eatery, args=("ryan",), name="eat_burgers")
        self.fries_eater = threading.Thread(target=self.eatery, args=("sophie",), name="eat_fries")
        self.burger_eater.start()
        self.fries_eater.start()
        self.burger_eater.join()
        self.fries_eater.join()
        assert self.sequence == ["sophie", "ryan", "sophie", "ryan", "sophie"]

class TestBlockingWeave(object):
    """This is a simple test of the same concept being done in a single method, with artificial blocking"""
    def eat_burgers(self, name):
        """eat burgers, one at a time, and add fries to the end when you do - whine if there aren't any"""
        with self.items_lock:
            if self.items_to_eat[0] == "burger":
                self.items_to_eat.pop(0)
                self.sequence.append(name)
                self.items_to_eat.append("fries")
            else:
                raise ValueError("I only want to see burgers!")

    def eat_fries(self, name):
        """eat as many fries at once as you can - and whine if there aren't any"""
        with self.items_lock:
            if not self.items_to_eat:
                return
            if self.items_to_eat[0] == "fries":
                self.sequence.append(name)
            else:
                raise ValueError("I only want to see fries!")
            while self.items_to_eat and self.items_to_eat[0] == "fries":
                self.items_to_eat.pop(0)

    def single_seat_eatery(self, name):
        """A method that can be entered by multiple threads, and decides what to do as it processes the queue depending on which thread is active, blocking the others along the way"""
        with ThreadWeave.only_thread_blocking('eat_fries', 'first_fries') as StatementSkipped.detector:
            self.eat_fries(name)
        with ThreadWeave.only_thread_blocking('eat_burgers') as StatementSkipped.detector:
            self.eat_burgers(name)
        with ThreadWeave.only_thread_blocking('eat_fries') as StatementSkipped.detector:
            self.eat_fries(name)
        with ThreadWeave.only_thread_blocking('eat_burgers') as StatementSkipped.detector:
            self.eat_burgers(name)
        with ThreadWeave.only_thread_blocking('eat_fries', 'third_fries') as StatementSkipped.detector:
            self.eat_fries(name)

    def test_each_complete(self):
        self.items_lock = threading.Lock()
        self.items_to_eat = ["fries", "burger", "fries", "burger"]
        self.sequence = []
        self.burger_eater = threading.Thread(target=self.single_seat_eatery, args=("ryan",), name="eat_burgers")
        self.fries_eater = threading.Thread(target=self.single_seat_eatery, args=("sophie",), name="eat_fries")
        self.burger_eater.start()
        self.fries_eater.start()
        self.burger_eater.join()
        self.fries_eater.join()
        assert self.sequence == ["sophie", "ryan", "sophie", "ryan", "sophie"]

