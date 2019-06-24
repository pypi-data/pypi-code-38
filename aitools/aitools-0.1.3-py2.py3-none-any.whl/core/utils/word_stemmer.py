from aitools.utils import constant

import re


class WordStemmer:

    def __init__(self, rule_tuple=None, strip_prefix_flag=False):
        """
            Create an instance of the stemmer.
        """
        # Setup an empty rule dictionary - this will be filled in later
        self.rule_dictionary = {}
        # Check if a user wants to strip prefix
        self._strip_prefix = strip_prefix_flag
        # Check if a user wants to use his/her own rule tuples.
        self._rule_tuple = rule_tuple if rule_tuple else constant.STEMMER_RULE_TUPLE

    def parse_rules(self, rule_tuple=None):
        """
            Validate the set of rules used in this stemmer.

            If this function is called as an individual method, without using stem
            method, rule_tuple argument will be compiled into self.rule_dictionary.
            If this function is called within stem, self._rule_tuple will be used.
        """
        # If there is no argument for the function, use class' own rule tuple.
        rule_tuple = rule_tuple if rule_tuple else self._rule_tuple
        valid_rule = re.compile(constant.REGEX_STEMMER_PARSING)
        # Empty any old rules from the rule set before adding new ones
        self.rule_dictionary = {}

        for rule in rule_tuple:
            if not valid_rule.match(rule):
                raise ValueError("The rule {0} is invalid".format(rule))
            first_letter = rule[0:1]
            if first_letter in self.rule_dictionary:
                self.rule_dictionary[first_letter].append(rule)
            else:
                self.rule_dictionary[first_letter] = [rule]

    def stem(self, word):
        """
            Stem a word using the Lancaster stemmer.
        """
        # Lower-case the word, since all the rules are lower-cased
        word = word.lower()
        word = strip_prefix(word) if self._strip_prefix else word

        # Save a copy of the original word
        intact_word = word

        # If rule dictionary is empty, parse rule tuple.
        if not self.rule_dictionary:
            self.parse_rules()

        return self.do_stemming(word, intact_word)

    def do_stemming(self, word, intact_word):
        """
            Perform the actual word stemming
        """

        valid_rule = re.compile(constant.REGEX_STEMMER_STEMMING)

        proceed = True

        while proceed:

            # Find the position of the last letter of the word to be stemmed
            last_letter_position = get_last_letter(word)

            # Only stem the word if it has a last letter and a rule matching that last letter
            if (
                last_letter_position < 0
                or word[last_letter_position] not in self.rule_dictionary
            ):
                proceed = False

            else:
                rule_was_applied = False

                # Go through each rule that matches the word's final letter
                for rule in self.rule_dictionary[word[last_letter_position]]:
                    rule_match = valid_rule.match(rule)
                    if rule_match:
                        (
                            ending_string,
                            intact_flag,
                            remove_total,
                            append_string,
                            cont_flag,
                        ) = rule_match.groups()

                        # Convert the number of chars to remove when stemming
                        # from a string to an integer
                        remove_total = int(remove_total)

                        # Proceed if word's ending matches rule's word ending
                        if word.endswith(ending_string[::-1]):
                            if intact_flag:
                                if word == intact_word and is_acceptable(
                                    word, remove_total
                                ):
                                    word = apply_rule(
                                        word, remove_total, append_string
                                    )
                                    rule_was_applied = True
                                    if cont_flag == '.':
                                        proceed = False
                                    break
                            elif is_acceptable(word, remove_total):
                                word = apply_rule(
                                    word, remove_total, append_string
                                )
                                rule_was_applied = True
                                if cont_flag == '.':
                                    proceed = False
                                break
                # If no rules apply, the word doesn't need any more stemming
                if not rule_was_applied:
                    proceed = False
        return word

    def __repr__(self):
        return '<WordStemmer>'


def get_last_letter(word):
    """
        Get the zero-based index of the last alphabetic character in this string
    """
    last_letter = -1
    for position in range(len(word)):
        if word[position].isalpha():
            last_letter = position
        else:
            break
    return last_letter


def is_acceptable(word, remove_total):
    """
        Determine if the word is acceptable for stemming.
    """
    word_is_acceptable = False
    # If the word starts with a vowel, it must be at least 2
    # characters long to be stemmed
    if word[0] in "aeiouy":
        if len(word) - remove_total >= 2:
            word_is_acceptable = True
    # If the word starts with a consonant, it must be at least 3
    # characters long (including one vowel) to be stemmed
    elif len(word) - remove_total >= 3:
        if word[1] in "aeiouy":
            word_is_acceptable = True
        elif word[2] in "aeiouy":
            word_is_acceptable = True
    return word_is_acceptable


def apply_rule(word, remove_total, append_string):
    """
        Apply the stemming rule to the word
    """
    # Remove letters from the end of the word
    new_word_length = len(word) - remove_total
    word = word[0:new_word_length]

    # And add new letters to the end of the truncated word
    if append_string:
        word += append_string
    return word


def strip_prefix(word):
    """
        Remove prefix from a word.
        This function originally taken from Whoosh.
    """
    for prefix in (
        "kilo",
        "micro",
        "milli",
        "intra",
        "ultra",
        "mega",
        "nano",
        "pico",
        "pseudo",
    ):
        if word.startswith(prefix):
            return word[len(prefix) :]
    return word
