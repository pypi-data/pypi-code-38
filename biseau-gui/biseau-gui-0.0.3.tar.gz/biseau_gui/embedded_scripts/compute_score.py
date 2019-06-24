
from itertools import combinations

NAME = "Ranker"
OUTPUTS = {"score/3"}

def run_on(models, *, multiplier:float=2):
    for model in models:
        for (geneA, valA), (geneB, valB) in combinations(model.get('gene', ()), r=2):
            score = abs(float(valA) - float(valB)) * float(multiplier)
            yield f'score({geneA},{geneB},"{score}").'
