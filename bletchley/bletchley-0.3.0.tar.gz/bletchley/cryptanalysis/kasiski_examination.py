""" """
from collections import defaultdict


def kasiski_examination(ciphertext):
    """ """
    matches = defaultdict(list)
    length = 16  # len(ciphertext)
    id_counter = 0
    positions = []
    for i in range(length, 4, -1):
        for x in range(len(ciphertext)):
            search_start = x
            search_size = i
            search_string = ciphertext[
                search_start:search_start + search_size]
            for y in range(search_start + 1, len(ciphertext)):
                if ciphertext[y:y+search_size] == search_string:
                    if x not in positions:
                        positions.append(positions)
                        matches[str(i)].append({"start": x, "position": y})
                        id_counter += 1
    print('-'*12)
    max_search_size = 0
    predicted_search_size = 0
    for i in range(4, length):
        if (len(matches[str(i)])) > max_search_size:
            max_search_size = len(matches[str(i)])
            predicted_search_size = i

        print(i, len(matches[str(i)]))

    print('-'*12)
    print(predicted_search_size)
    return predicted_search_size
