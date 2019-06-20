import re

class PhraseTemplate:
    def __init__(self, ID=None, TempStrArr = None, TempNLPArr = None, TypeArr = None, Inclinations=None, Values=None, ValuesCZ=None, MatchPattern = None):
        self.ID = ID
        self.TempStr = TempStrArr
        self.TempToNLP = TempNLPArr
        self.Type = TypeArr
        self.Inclinations = Inclinations

        self.tokens_specs = [  # Regex collection for signals  that can occur in conditions
            ("SinO", r"(?P<subject>\w+)in(?P<object>\w+)",r"(?P<subject>\w+)in(?P<object>\w+)",[2,3]),
            ("SatO", r"(?P<subject>\w+)at(?P<object>\w+)",r"(?P<subject>\w+)in(?P<object>\w+)",[2,3]),
            ("SonO", r"(?P<subject>\w+)on(?P<object>\w+)",r"(?P<subject>\w+)in(?P<object>\w+)",[2,3]),
            ("SProgramNum", r"robot(?P<robotName>\w+)programnumber",r"(?P<subject>\w+)in(?P<object>\w+)",[2,3]),
            ("ProgramStarted", r"programstarted",r"(?P<subject>\w+)in(?P<object>\w+)",[2,3]),
            ("ProgramEnded", r"programended",r"(?P<subject>\w+)in(?P<object>\w+)",[2,3])]

        def matchPhrase(self, phrase):
            # totalPhr = []
            # totalTemp = []
            # re.compile(r"robot(?P<robotName>\w+)programnumber", re.IGNORECASE)
            for phr in phrase.values():
                totalPhr += phr
            for str,temp in self.tokens_specs:
                totalTemp += temp
            print("Is {} matching {}?".format(totalPhr, totalTemp))  # (phrase, self.TempStr))
            match = self.TempStr.search(phr)

            # if set(self.MatchPattern) == common:
            #     match = True
            # else:
            #     math = False
            return match





if __name__ == "__main__":

    # phrases are list of SignalPhrase objects
    # mytemplates are list of PhraseTemplate objects obtained from
    mytemplates = PhraseTemplateFactory.make_phrase_dict()
    for phrase in phrases.values():
        phrase.split_phrase()

        PhraseTemp = PhraseTemplate()
        for template in mytemplates.values():
            matching = template.matchPhrase(phrase.splitphrase)
            print(matching)
            if matching:
                phrase.phrasetemplate = template
                # phrase.joinphrase = phrase
                break