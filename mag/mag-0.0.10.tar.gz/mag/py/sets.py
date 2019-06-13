from itertools import combinations

def subsets(setnames:list) -> list:
    ''' Gives the 2^n subsets for every set in setnames

    Args:
        setnames (list): a list of elements, where each element corresponds to
            the name of a set. e.g. ['A', 'B', ..., 'Z']
    Returns:
        subsets (list): a list of tuples, where each tuple contains the set
            names corresponding to the sets in that subset

            e.g. [(), (A, ), (B, ), ..., (A, B, ), ... (A, B, ..., Z)]
    '''
    number_of_sets = len(setnames)
    return [
        combination
        for combination_index in range(number_of_sets)
        for combination in list(combinations(setnames, combination_index))
    ] + [tuple(setnames)]

def partitions_by_length(partitions:list):
    '''Groups partitions by number of sets in each partition

    Args:
        partitions (list): a list of lists, where each sublist represents a
            partititon and each item therein corresponds to the name of a set.

            e.g. the output of subsets

    Returns:

        partitons_by_length (dict): {num: partitons} pairs where num is an int
            specifiy the number of sets in each partition, and partitions is
            a list containing all partitions with num sets.

    '''
    grouped = {}
    for partition in partitions:
        cardinality = len(partition)
        if cardinality not in grouped:
            grouped[cardinality] = []
        grouped[cardinality].append(partition)
    return grouped

def upset_elements(sets:dict, domain:set=set({})) -> dict:
    '''Gives the elements unique to each ~region~ of the venn diagram

    Args:
        sets (dict): the pair of {setname (str): elements (list)} for which to
            compute on

        domain (set): all the elements, including those which may not be seen in
            the passed sets. By default, an empty set.

    Returns:
        elements_unique_to_comparisons (dict): a dict containing the pair of
            {comparison (tuple): elements (list)}, where comparison is a tuple
            of setnames (keys from sets), e.g. ('A', 'B',) indicating the
            comparison made.

    '''
    setnames = list(sets.keys())
    # returns partitions of setnames in increasing number of sets, e.g.
    # [(), (A, ), (B, ), ..., (A, B, ), ... (A, B, ..., Z)]
    comparisons = subsets(setnames)
    comparisons.reverse()

    # group each comparison by how many sets in each comparisons e.g.
    # work our way from the inner most of the venn diagram to the outer most
    grouped_comparisons = partitions_by_length(comparisons)

    # results
    elements_unique_to_comparisons = {}

    # elements we have already seen
    seen = set({})

    # start with the intersection of all sets and work our way to the empty set
    for n_sets in range(len(setnames), -1, -1):

        partitions_with_n_sets = grouped_comparisons[n_sets]
        current_comparisons = [
            [
                # list of elements for each set in the current comparison
                sets[name] for name in comparison
            ]  for comparison in partitions_with_n_sets
            # where each partition of n sets is a comparison to make
        ]

        # the empty set
        if partitions_with_n_sets == [()]:
            # elements unique to the empty set is anything in the domain not
            # already seen
            elements_unique_to_comparisons.update({
                (): domain.difference(seen)
            })
            # nothing else to do
            continue

        intersections = [
            # elements shared across the sets in the comparison
            set.intersection(*comparison_sets)
            # for all comparisons with n sets in them
            for comparison_sets in current_comparisons
        ]

        uniques = [
            # filter out elements already seen
            intersection.difference(seen)
            for intersection in intersections
        ]

        elements_unique_to_comparisons.update(
            dict(
                list(
                    zip(
                        partitions_with_n_sets, uniques
                    ) # tuples of (sets in current partition, unique elements)
                ) # cast as a list
            ) # cast as a dict
        ) # update our results

        just_seen = set.union(*uniques)
        seen.update(just_seen)

    return elements_unique_to_comparisons
