
__seed__ = ['file_parser']


def grade_file_parser(student_fuction):
    """ Test solution to "Odds and Ends"

    Parameters
    ----------
    student_fuction: Callable[str]
        Student solution function.
    """
    from bwsi_grader.print import print_passed
    from bwsi_grader import compare_functions
    from hashlib import sha224
    import numpy as np
    import os

    def write_test_file(fname, list_length=10, items_per_entry=3):
        """ Write test file used to evaluate student function.

        Parameters
        ----------
        fname: str
            File name.

        list_length: int, optional (default=10)
            Length of file.

        items_per_entry: int, optional (default=3)
            Max number of entries (food-category pairs) per line.
        """
        foods = {'dessert': ['cake', 'cookies', 'ice cream', 'candy'],
                 'vegetable': ['carrots', 'spinach', 'broccoli', 'kale'],
                 'meat': ['chicken', 'pork', 'steak', 'tuna'],
                 'fruit': ['apples', 'peaches', 'pears', 'bananas']}

        entries = []
        for key, values in foods.items():
            for value in values:
                entries.extend([f'{value}: {key}'])

        final_entries = []
        for i in range(list_length):
            choices = np.random.choice(entries, np.random.randint(1, items_per_entry), replace=False)
            final_entries.append(', '.join(choices))

        with open(fname, 'w') as f:
            f.write('\n'.join(final_entries))

    def solution(file_path):
        """ Read in survey and determine the most common food of each type.

        Parameters
        ----------
        file_path : str
            Path to text file containing favorite food survey responses.

        Returns
        -------
        Dict[str, str]
            Dictionary with the key being food type and value being food.
        """
        from collections import Counter
        from itertools import chain

        with open(file_path, 'r') as f:
            # read correctly formatted lines
            entries = list(filter(lambda x: ': ' in x, chain(*[entry.split(', ') for entry in f.read().splitlines()])))

        responses = {}
        for entry in entries:
            food, food_type = entry.split(': ')
            responses.setdefault(food_type, []).append(food)

        return {k: Counter(sorted(v)).most_common()[0][0] for (k, v) in responses.items()}

    # generate random files and compare results
    foods_file = 'favorite-foods.txt'
    try:
        for i in range(100):
            write_test_file(foods_file, list_length=np.random.randint(1, 50), items_per_entry=np.random.randint(2, 5))
            compare_functions(student=student_fuction, soln=solution, fn_args=(foods_file,))
    finally:
        os.remove(foods_file)

    print_passed(sha224(str.encode(__seed__[0])).hexdigest())
