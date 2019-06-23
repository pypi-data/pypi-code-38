from enum import Enum


class Feed(Enum):
    SMOOTHSTREAMS = 'https://fast-guide.smoothstreams.tv/feed-new-latest.zip'
    # FOG = 'https://fast-guide.smoothstreams.tv/altepg/feedall1.json'


class Quality(Enum):
    HD = 1
    HQ = 2
    LQ = 3

    def __str__(self):
        return str(self.value)


class Protocol(Enum):
    HLS = 1
    RTMP = 2
    MPEG = 3

    def __str__(self):
        return self.value


class Server(Enum):
    EU_MIX = 'deu.smoothstreams.tv'

    EU_DE_MIX = 'deu-de.smoothstreams.tv'

    EU_NL_MIX = 'deu-nl.smoothstreams.tv'
    EU_NL1 = 'deu-nl1.smoothstreams.tv'
    EU_NL2 = 'deu-nl2.smoothstreams.tv'
    EU_NL3 = 'deu-nl3.smoothstreams.tv'
    EU_NL4 = 'deu-nl4.smoothstreams.tv'
    EU_NL5 = 'deu-nl5.smoothstreams.tv'

    EU_UK_MIX = 'deu-uk.smoothstreams.tv'
    EU_UK1 = 'deu-uk1.smoothstreams.tv'
    EU_UK2 = 'deu-uk2.smoothstreams.tv'

    NA_EAST_MIX = 'dna.smoothstreams.tv'
    NA_WEST_MIX = 'dnaw.smoothstreams.tv'

    NA_EAST_NJ = 'dnae1.smoothstreams.tv'
    NA_EAST_VA = 'dnae2.smoothstreams.tv'
    NA_EAST_MTL = 'dnae3.smoothstreams.tv'
    NA_EAST_TOR = 'dnae4.smoothstreams.tv'
    NA_EAST_NY = 'dnae6.smoothstreams.tv'

    NA_WEST_PHX = 'dnaw1.smoothstreams.tv'
    NA_WEST_LA = 'dnaw2.smoothstreams.tv'
    NA_WEST_CHI_1 = 'dnaw3.smoothstreams.tv'
    NA_WEST_CHI_2 = 'dnaw4.smoothstreams.tv'

    ASIA_SG_01 = 'dAP1.smoothstreams.tv'
    ASIA_SG_02 = 'dAP2.smoothstreams.tv'
    ASIA_SG_03 = 'dAP3.smoothstreams.tv'
    ASIA_MIX = 'dAP.smoothstreams.tv'


    def __str__(self):
        return self.value


class Service(Enum):
    LIVE247 = 'view247'
    STARSTREAMS = 'viewss'
    STREAMTVNOW = 'viewstvn'
    MMATV = 'viewmmasr'
