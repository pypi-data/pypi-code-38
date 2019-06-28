import abc

from combcov.exact_cover import ExactCover


class CombCov():

    def __init__(self, root_object, max_elmnt_size):
        self.root_object = root_object
        self.max_elmnt_size = max_elmnt_size
        self._enumerate_all_elmnts_up_to_max_size()
        self._create_binary_strings_from_rules()

    def _enumerate_all_elmnts_up_to_max_size(self):
        elmnts = []
        self.enumeration = [None] * (self.max_elmnt_size + 1)
        for n in range(self.max_elmnt_size + 1):
            elmnts_of_length_n = self.root_object.get_elmnts(of_size=n)
            self.enumeration[n] = len(elmnts_of_length_n)
            elmnts.extend(elmnts_of_length_n)

        print("[INFO] Total of {} elements of size up to {}".format(
            len(elmnts), self.max_elmnt_size))
        print("[INFO] Enumeration: {}".format(self.enumeration))

        self.elmnts_dict = {
            string: nr for nr, string in enumerate(elmnts, start=0)
        }

    def _create_binary_strings_from_rules(self):
        string_to_cover = 2 ** len(self.elmnts_dict) - 1
        print("[INFO] Bitstring to cover: {} ".format(string_to_cover))

        self.rules = []
        self.bitstrings = []
        self.bitstring_to_rules_dict = {}
        self.rules_to_bitstring_dict = {}

        for rule in self.root_object.get_subrules():
            if rule in self.rules:
                rule_is_good = False
            else:
                rule_is_good = True
                binary_string = 0

            for elmnt_size in range(self.max_elmnt_size + 1):
                if not rule_is_good:
                    break

                seen_elmnts = set()
                for elmnt in rule.get_elmnts(of_size=elmnt_size):
                    if elmnt not in self.elmnts_dict or elmnt in seen_elmnts:
                        rule_is_good = False
                        break
                    else:
                        seen_elmnts.add(elmnt)
                        binary_string += 2 ** (self.elmnts_dict[elmnt])

                # Throwing out single-rule covers
                if binary_string == string_to_cover:
                    rule_is_good = False

            if rule_is_good:
                self.rules.append(rule)
                self.rules_to_bitstring_dict[rule] = binary_string

                # ToDo: Use defaultdict for more readable syntax
                if binary_string not in self.bitstring_to_rules_dict:
                    self.bitstrings.append(binary_string)
                    self.bitstring_to_rules_dict[binary_string] = [rule]
                else:
                    self.bitstring_to_rules_dict[binary_string].append(rule)

    def solve(self):
        print("[INFO] Trying to find a cover for {} using elements up to size "
              "{}.".format(self.root_object, self.max_elmnt_size))
        self.ec = ExactCover(self.bitstrings, len(self.elmnts_dict))
        self.solutions_indices = self.ec.exact_cover()

    def get_solutions(self):
        solutions = []
        for solution_indices in self.solutions_indices:
            solution = [
                self.bitstring_to_rules_dict[self.bitstrings[bitstring_index]][
                    0] for bitstring_index in solution_indices]
            solutions.append(solution)

        return solutions


class Rule(abc.ABC):
    @abc.abstractmethod
    def get_elmnts(self, of_size):
        raise NotImplementedError

    @abc.abstractmethod
    def get_subrules(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _key(self):
        raise NotImplementedError

    @abc.abstractmethod
    def __str__(self):
        raise NotImplementedError

    def __hash__(self):
        return hash(self._key())

    def __eq__(self, other):
        return isinstance(self, type(other)) and self._key() == other._key()
