from typing import List

def levenshteinDistance(s1:str, s2:str):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]

def closest(word:str, words:List[str], threshold:float=0.5)->str:
    best_score, best_candidate = 1, None
    for candidate in words:
        score = levenshteinDistance(word, candidate)/max(len(word), len(candidate))
        if score < best_score and score < threshold:
            best_score = score
            best_candidate = candidate
    return best_candidate