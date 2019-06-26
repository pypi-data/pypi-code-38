import logging
import re

import spacy
from spacy.cli.download import download as spacy_download

logger = logging.getLogger(__name__)


class SSML:
    INTERPRET_AS = ['cardinal', 'ordinal', 'number_digit', 'date', 'time', 'telephone']

    spacy_supported_ner = ['DATE',
                           'TIME',
                           'PERCENT',
                           'MONEY',
                           'QUANTITY',
                           'ORDINAL',
                           'CARDINAL']

    ner_interpret_dict = {
        'CARDINAL': 'cardinal',
        'PERCENT': 'cardinal',
        'MONEY': 'cardinal',
        'QUANTITY': 'cardinal',

        'ORDINAL': 'ordinal',

        # below two are identify be regex
        # 'CARDINAL': 'number_digit',
        # 'CARDINAL': 'telephone',

        'DATE': 'date',
        'TIME': 'time',
    }

    DATE_FORMAT = ['mdy', 'dmy', 'ymd', 'md', 'dm', 'ym', 'my', 'd', 'm', 'y']

    TIME = ['hms12', 'hms23']

    def __init__(self, model_name="en_core_web_sm"):
        """
        Initialize a SSML instance. English spacy model will loaded if no spacy model specified.
        :param model_name: Spacy model name.
        """
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            logger.info('download AI model...')
            # below code will download AI model from SpaCy, usually the size is about 11+M
            spacy_download(model_name)
            self.nlp = spacy.load(model_name)

    def dump(self, doc):
        """
        Dump a document to ssml.
        :param doc:
        :return:
        """
        nlp_doc = self.nlp(doc)

        tel_pattern = re.compile(r'(\+*\d+)*([ |(])*(\d{3})[^\d]*(\d{3})[^\d]*(\d{4})')
        tel_ents = re.finditer(tel_pattern, doc)

        zip_pattern = re.compile(r'.*(\d{5}(-\d{4})?)$')
        zip_ents = re.finditer(zip_pattern, doc)

        num_ents = [item for item in nlp_doc.ents if
                    item.label_ in self.ner_interpret_dict.keys() and self.ner_interpret_dict[
                        item.label_] in self.INTERPRET_AS]

        num_ents.reverse()
        revised_doc = nlp_doc.text
        for item in num_ents:
            item_text = item.string
            item_label = item.label_

            if (not self.is_telephone(item, tel_ents)) or (not self.is_zip(item, zip_ents)):
                if item_label in ['CARDINAL',
                                  'PERCENT',
                                  'MONEY',
                                  'QUANTITY']:
                    item_label = 'cardinal'
                elif item_label in ['ORDINAL']:
                    item_label = 'ordinal'
                elif item_label in ['DATE']:
                    item_label = 'date'
                elif item_label in ['TIME']:
                    item_label = 'time'

                entity = self._say_as(item_text, item_label)
                revised_doc = revised_doc[:item.start_char] + entity + revised_doc[item.end_char:]

        revised_doc = tel_pattern.sub(lambda x: self._say_as(x, 'telephone'), revised_doc)
        revised_doc = zip_pattern.sub(lambda x: self._say_as(x, 'number_digit'), revised_doc)

        return revised_doc

    # todo:
    def is_telephone(self, item, telephone_ents):
        pass

    # todo:
    def is_zip(self, item, zip_ents):
        pass

    def _say_as(self, word, interpret, interpred_format=None):
        if word is None:
            raise TypeError('Parameter word must not be None')
        if interpret is None:
            raise TypeError('Parameter interpret must not be None')
        if interpret not in self.INTERPRET_AS:
            raise TypeError('Unknown interpret as %s' % str(interpret))
        if interpred_format is not None and interpred_format not in self.DATE_FORMAT:
            raise ValueError('Unknown date format %s' % str(interpred_format))
        if interpred_format is not None and interpret != 'date':
            raise ValueError('Date format %s not valid for interpret as %s' % (str(interpred_format), str(interpret)))

        format_ssml = '' if interpred_format is None else " format=\"%s\"" % interpred_format

        return "<say-as interpret-as=\"%s\"%s>%s</say-as>" % (interpret, format_ssml, str(word))


def ssml_interactive_process():
    ssml = SSML()
    doc = '''NEW YORK, May 30 (Reuters) - World stock markets climbed for the first time this week on Thursday, giving pause to a multiday selloff on fears of an escalating trade war between the United States and China that has pushed investors into safe-haven bonds and the U.S. dollar.

        Signs that the year-long trade dispute between the U.S. and China will not be resolved quickly and concerns over its impact on global growth have roiled markets, sending stock indexes into their most turbulent month of the year so far.

        "We oppose a trade war but are not afraid of a trade war," Chinese Vice Foreign Minister Zhang Hanhui said on Thursday in Beijing, when asked about the tensions with the United States.

        "This kind of deliberately provoking trade disputes is naked economic terrorism, economic chauvinism, economic bullying."

        His comments followed reports from Chinese newspapers that Beijing could use its rare earth supplies as a bargaining chip https://www.reuters.com/article/us-usa-china-rareearth-explainer/explainer-chinas-rare-earth-supplies-could-be-vital-bargaining-chip-in-u-s-trade-war-idUSKCN1T00EK to strike back at Washington after U.S. President Donald Trump remarked he was "not yet ready" to make a deal with China over trade.

        Rare earths are elements used in production in industries such as renewable energy technology, oil refinery, electronics and glass. There have been concerns that China, a key exporter of rare earths to the United States, may use that fact as leverage in the trade spat.

        "People are trying to figure out how much of the bad news is already priced in. The trade war looks like it might dampen growth but not enough to throw us into a recession," said Scott Brown, chief economist at Raymond James in St. Petersburg, Florida.

        "There has been talk about the Fed possibly cutting rates and that is a little bit positive for the stock market."

        MSCI's gauge of stocks across the globe gained 0.34%.

        On Wall Street, the Dow Jones Industrial Average rose 65.06 points, or 0.26%, to 25,191.47, the S&P 500 gained 12.2 points, or 0.44%, to 2,795.22 and the Nasdaq Composite added 39.48 points, or 0.52%, to 7,586.79.

        The pan-European STOXX 600 index rose 0.48%.

        German Bund yields climbed for the first time in four days after hitting record lows and Treasury yields climbed. Money markets are now pricing in roughly two U.S. rate cuts by the start of next year as trade worries weigh on the global economy.

        The dollar index, tracking the greenback against six major currencies, was steady at 98.113 and in reach of a two-year peak of 98.371 set last week.

        "The strength in the dollar is surprising given that markets are now expecting multiple rate cuts by 2020," Commerzbank FX strategist Ulrich Leuchtmann said.

        Oil prices traded in a tight range after an industry report showed a decline in U.S. crude inventories that exceeded analyst expectations.

        That followed volatile trading on Wednesday, when oil prices fell to near three-month lows at one point as trade war fears gripped the commodity markets.

        U.S. crude futures were up 0.25% at $58.96 per barrel after brushing $56.88 the previous day, their lowest since March 12. Brent crude was flat at $69.13 per barrel.

        (Reporting by David Randall; Editing by Bernadette Baum)'''
    process_command = input("Want to ssml with default text?\n(yes/no/exit):")

    if process_command.lower() in ['yes', 'y']:
        print(ssml.dump(doc))
    elif process_command.lower() in ['no', 'n']:
        print("ssml is:\n%s" % ssml.dump(input("Input the text want to convert to ssml:\n")))
    elif process_command.lower() in ['exit']:
        print("exit successfully.")
    else:
        ssml_interactive_process()


if __name__ == '__main__':
    ssml_interactive_process()
