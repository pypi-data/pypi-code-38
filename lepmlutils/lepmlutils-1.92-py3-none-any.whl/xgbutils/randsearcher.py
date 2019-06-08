import random
from .searcher import Searcher
from typing import Dict

class RandSearcher(Searcher):
    MAX_ITERATIONS = 60

    def __init__(self, params: Dict):
        self.params = params
        self.finished_iterations = 0
    
    def __iter__(self) -> Searcher:
        return self
        
    def __next__(self) -> Dict:
        if self.finished_iterations >= self.MAX_ITERATIONS:
            raise StopIteration
        
        self.finished_iterations += 1
        return self.random_selection()

    def random_selection(self) -> Dict:
        selection = {}
        for key, values in self.params.items():
            selection[key] = random.choice(values)

        return selection