import enum
from collections import namedtuple


AgentTypeInfo = namedtuple('AgentTypeInfo', ['agent_type', 'api_endpoint'])


class AgentType(enum.Enum):
    """
    Enumeration for the agent_agent_type controlled value list. The values of
    this enum use the AgentTypeInfo named tuple, wrapping the enumeration
    value and the API endpoint for the particular agent type.
    """

    # pylint: disable=E1101
    @property
    def agent_type(self) -> str:
        return self.value.agent_type

    @property
    def api_endpoint(self) -> str:
        return self.value.api_endpoint
    # pylint: enable=E1101

    PERSON = AgentTypeInfo('agent_person', '/agents/people')

    FAMILY = AgentTypeInfo('agent_family', '/agents/families')

    CORPORATE_ENTITY = AgentTypeInfo(
        'agent_corporate_entity', 
        '/agents/corporate_entities'
    )

    SOFTWARE = AgentTypeInfo('software', '/agents/software')


class AgentNameOrder(enum.Enum):
    INVERTED = 'inverted'
    DIRECT = 'direct'


class LinkedAgentRole(enum.Enum):
    CREATOR = 'creator'
    SOURCE = 'source'
    SUBJECT = 'subject'


class LinkedAgentArchivalRecordRelator(enum.Enum):
    r"""
    Enumeration for the default values of ArchivesSpace enumeration 1.

    This enumeration was generated from
    http://localhost:8080/enumerations?id=1 using a terrible jQuery statement.
    """

    ACTOR = 'act'
    ADAPTER = 'adp'
    AUTHOR_OF_AFTERWORD_COLOPHON_ETC_ = 'aft'
    ANALYST = 'anl'
    ANIMATOR = 'anm'
    ANNOTATOR = 'ann'
    BIBLIOGRAPHIC_ANTECEDENT = 'ant'
    APPLICANT = 'app'
    AUTHOR_IN_QUOTATIONS_OR_TEXT_ABSTRACTS = 'aqt'
    ARCHITECT = 'arc'
    ARTISTIC_DIRECTOR = 'ard'
    ARRANGER = 'arr'
    ARTIST = 'art'
    ASSIGNEE = 'asg'
    ASSOCIATED_NAME = 'asn'
    ATTRIBUTED_NAME = 'att'
    AUCTIONEER = 'auc'
    AUTHOR_OF_DIALOG = 'aud'
    AUTHOR_OF_INTRODUCTION_ETC_ = 'aui'
    AUTHOR_OF_SCREENPLAY_ETC_ = 'aus'
    AUTHOR = 'aut'
    BINDING_DESIGNER = 'bdd'
    BOOKJACKET_DESIGNER = 'bjd'
    BOOK_DESIGNER = 'bkd'
    BOOK_PRODUCER = 'bkp'
    BLURB_WRITER = 'blw'
    BINDER = 'bnd'
    BOOKPLATE_DESIGNER = 'bpd'
    BOOKSELLER = 'bsl'
    CONCEPTOR = 'ccp'
    CHOREOGRAPHER = 'chr'
    COLLABORATOR = 'clb'
    CLIENT = 'cli'
    CALLIGRAPHER = 'cll'
    COLORIST = 'clr'
    COLLOTYPER = 'clt'
    COMMENTATOR = 'cmm'
    COMPOSER = 'cmp'
    COMPOSITOR = 'cmt'
    CONDUCTOR = 'cnd'
    CINEMATOGRAPHER = 'cng'
    CENSOR = 'cns'
    CONTESTANT_APPELLEE = 'coe'
    COLLECTOR = 'col'
    COMPILER = 'com'
    CONSERVATOR = 'con'
    CONTESTANT = 'cos'
    CONTESTANT_APPELLANT = 'cot'
    COVER_DESIGNER = 'cov'
    COPYRIGHT_CLAIMANT = 'cpc'
    COMPLAINANT_APPELLEE = 'cpe'
    COPYRIGHT_HOLDER = 'cph'
    COMPLAINANT = 'cpl'
    COMPLAINANT_APPELLANT = 'cpt'
    CREATOR = 'cre'
    CORRESPONDENT = 'crp'
    CORRECTOR = 'crr'
    CONSULTANT = 'csl'
    CONSULTANT_TO_A_PROJECT = 'csp'
    COSTUME_DESIGNER = 'cst'
    CONTRIBUTOR = 'ctb'
    CONTESTEE_APPELLEE = 'cte'
    CARTOGRAPHER = 'ctg'
    CONTRACTOR = 'ctr'
    CONTESTEE = 'cts'
    CONTESTEE_APPELLANT = 'ctt'
    CURATOR_OF_AN_EXHIBITION = 'cur'
    COMMENTATOR_FOR_WRITTEN_TEXT = 'cwt'
    DISTRIBUTION_PLACE = 'dbp'
    DEFENDANT = 'dfd'
    DEFENDANT_APPELLEE = 'dfe'
    DEFENDANT_APPELLANT = 'dft'
    DEGREE_GRANTOR = 'dgg'
    DISSERTANT = 'dis'
    DELINEATOR = 'dln'
    DANCER = 'dnc'
    DONOR = 'dnr'
    DEPICTED = 'dpc'
    DEPOSITOR = 'dpt'
    DRAFTSMAN = 'drm'
    DIRECTOR = 'drt'
    DESIGNER = 'dsr'
    DISTRIBUTOR = 'dst'
    DATA_CONTRIBUTOR = 'dtc'
    DEDICATEE = 'dte'
    DATA_MANAGER = 'dtm'
    DEDICATOR = 'dto'
    DUBIOUS_AUTHOR = 'dub'
    EDITOR = 'edt'
    ENGRAVER = 'egr'
    ELECTRICIAN = 'elg'
    ELECTROTYPER = 'elt'
    ENGINEER = 'eng'
    ETCHER = 'etr'
    EVENT_PLACE = 'evp'
    APPRAISER = 'exp'
    FACSIMILIST = 'fac'
    FIELD_DIRECTOR = 'fld'
    FILM_EDITOR = 'flm'
    FORMER_OWNER = 'fmo'
    FUNDER = 'fnd'
    FIRST_PARTY = 'fpy'
    FORGER = 'frg'
    GEOGRAPHIC_INFORMATION_SPECIALIST = 'gis'
    GRAPHIC_TECHNICIAN = 'grt'
    HONOREE = 'hnr'
    HOST = 'hst'
    ILLUSTRATOR = 'ill'
    ILLUMINATOR = 'ilu'
    INSCRIBER = 'ins'
    INVENTOR = 'inv'
    INSTRUMENTALIST = 'itr'
    INTERVIEWEE = 'ive'
    INTERVIEWER = 'ivr'
    LABORATORY = 'lbr'
    LIBRETTIST = 'lbt'
    LABORATORY_DIRECTOR = 'ldr'
    LEAD = 'led'
    LIBELEE_APPELLEE = 'lee'
    LIBELEE = 'lel'
    LENDER = 'len'
    LIBELEE_APPELLANT = 'let'
    LIGHTING_DESIGNER = 'lgd'
    LIBELANT_APPELLEE = 'lie'
    LIBELANT = 'lil'
    LIBELANT_APPELLANT = 'lit'
    LANDSCAPE_ARCHITECT = 'lsa'
    LICENSEE = 'lse'
    LICENSOR = 'lso'
    LITHOGRAPHER = 'ltg'
    LYRICIST = 'lyr'
    MUSIC_COPYIST = 'mcp'
    METADATA_CONTACT = 'mdc'
    MANUFACTURE_PLACE = 'mfp'
    MANUFACTURER = 'mfr'
    MODERATOR = 'mod'
    MONITOR = 'mon'
    MARBLER = 'mrb'
    MARKUP_EDITOR = 'mrk'
    MUSICAL_DIRECTOR = 'msd'
    METAL_ENGRAVER = 'mte'
    MUSICIAN = 'mus'
    NARRATOR = 'nrt'
    OPPONENT = 'opn'
    ORIGINATOR = 'org'
    ORGANIZER_OF_MEETING = 'orm'
    OTHER = 'oth'
    OWNER = 'own'
    PATRON = 'pat'
    PUBLISHING_DIRECTOR = 'pbd'
    PUBLISHER = 'pbl'
    PROJECT_DIRECTOR = 'pdr'
    PROOFREADER = 'pfr'
    PHOTOGRAPHER = 'pht'
    PLATEMAKER = 'plt'
    PERMITTING_AGENCY = 'pma'
    PRODUCTION_MANAGER = 'pmn'
    PRINTER_OF_PLATES = 'pop'
    PAPERMAKER = 'ppm'
    PUPPETEER = 'ppt'
    PROCESS_CONTACT = 'prc'
    PRODUCTION_PERSONNEL = 'prd'
    PERFORMER = 'prf'
    PROGRAMMER = 'prg'
    PRINTMAKER = 'prm'
    PRODUCER = 'pro'
    PRODUCTION_PLACE = 'prp'
    PRINTER = 'prt'
    PROVIDER = 'prv'
    PATENT_APPLICANT = 'pta'
    PLAINTIFF_APPELLEE = 'pte'
    PLAINTIFF = 'ptf'
    PATENTEE = 'pth'
    PLAINTIFF_APPELLANT = 'ptt'
    PUBLICATION_PLACE = 'pup'
    RUBRICATOR = 'rbr'
    RECORDIST = 'rcd'
    RECORDING_ENGINEER = 'rce'
    RECIPIENT = 'rcp'
    REDAKTOR = 'red'
    RENDERER = 'ren'
    RESEARCHER = 'res'
    REVIEWER = 'rev'
    REPOSITORY = 'rps'
    REPORTER = 'rpt'
    RESPONSIBLE_PARTY = 'rpy'
    RESPONDENT_APPELLEE = 'rse'
    RESTAGER = 'rsg'
    RESPONDENT = 'rsp'
    RESPONDENT_APPELLANT = 'rst'
    RESEARCH_TEAM_HEAD = 'rth'
    RESEARCH_TEAM_MEMBER = 'rtm'
    SCIENTIFIC_ADVISOR = 'sad'
    SCENARIST = 'sce'
    SCULPTOR = 'scl'
    SCRIBE = 'scr'
    SOUND_DESIGNER = 'sds'
    SECRETARY = 'sec'
    SIGNER = 'sgn'
    SUPPORTING_HOST = 'sht'
    SINGER = 'sng'
    SPEAKER = 'spk'
    SPONSOR = 'spn'
    SECOND_PARTY = 'spy'
    SURVEYOR = 'srv'
    SET_DESIGNER = 'std'
    SETTING = 'stg'
    STORYTELLER = 'stl'
    STAGE_MANAGER = 'stm'
    STANDARDS_BODY = 'stn'
    STEREOTYPER = 'str'
    TECHNICAL_DIRECTOR = 'tcd'
    TEACHER = 'tch'
    THESIS_ADVISOR = 'ths'
    TRANSCRIBER = 'trc'
    TRANSLATOR = 'trl'
    TYPE_DESIGNER = 'tyd'
    TYPOGRAPHER = 'tyg'
    UNIVERSITY_PLACE = 'uvp'
    VIDEOGRAPHER = 'vdg'
    VOCALIST = 'voc'
    WRITER_OF_ACCOMPANYING_MATERIAL = 'wam'
    WOODCUTTER = 'wdc'
    WOOD_ENGRAVER = 'wde'
    WITNESS = 'wit'
    ABRIDGER = 'abr'
    ART_DIRECTOR = 'adi'
    APPELLEE = 'ape'
    APPELLANT = 'apl'
    AUTOGRAPHER = 'ato'
    BROADCASTER = 'brd'
    BRAILLE_EMBOSSER = 'brl'
    CASTER = 'cas'
    COLLECTION_REGISTRAR = 'cor'
    COURT_GOVERNED = 'cou'
    COURT_REPORTER = 'crt'
    DEGREE_SUPERVISOR = 'dgs'
    EDITOR_OF_COMPILATION = 'edc'
    EDITOR_OF_MOVING_IMAGE_WORK = 'edm'
    ENACTING_JURISDICTION = 'enj'
    FILM_DISTRIBUTOR = 'fds'
    FILM_DIRECTOR = 'fmd'
    FILMMAKER = 'fmk'
    FILM_PRODUCER = 'fmp'
    _GRT = '-grt'
    HOST_INSTITUTION = 'his'
    ISSUING_BODY = 'isb'
    JUDGE = 'jud'
    JURISDICTION_GOVERNED = 'jug'
    MEDIUM = 'med'
    MINUTE_TAKER = 'mtk'
    ONSCREEN_PRESENTER = 'osp'
    PANELIST = 'pan'
    PRAESES = 'pra'
    PRESENTER = 'pre'
    PRODUCTION_COMPANY = 'prn'
    PRODUCTION_DESIGNER = 'prs'
    RADIO_DIRECTOR = 'rdd'
    RADIO_PRODUCER = 'rpc'
    RESTORATIONIST = 'rsr'
    STAGE_DIRECTOR = 'sgd'
    SELLER = 'sll'
    TELEVISION_DIRECTOR = 'tld'
    TELEVISION_PRODUCER = 'tlp'
    VOICE_ACTOR = 'vac'
    WRITER_OF_ADDED_COMMENTARY = 'wac'
    WRITER_OF_ADDED_LYRICS = 'wal'
    WRITER_OF_ADDED_TEXT = 'wat'
    WRITER_OF_INTRODUCTION = 'win'
    WRITER_OF_PREFACE = 'wpr'
    WRITER_OF_SUPPLEMENTARY_TEXTUAL_CONTENT = 'wst'


class SubjectTermType(enum.Enum):
    CULTURAL_CONTEXT = 'cultural_context'
    FUNCTION = 'function'
    GENRE_FORM = 'genre_form'
    GEOGRAPHIC = 'geographic'
    OCCUPATION = 'occupation'
    STYLE_PERIOD = 'style_period'
    TECHNIQUE = 'technique'
    TEMPORAL = 'temporal'
    TOPICAL = 'topical'
    UNIFORM_TITLE = 'uniform_title'


@enum.unique
class Enumeration(enum.Enum):
    """
    Enumeration for the names of the controlled value lists in ArchivesSpace.
    """

    LINKED_AGENT_ARCHIVAL_RECORD_RELATORS = 1
    LINKED_EVENT_ARCHIVAL_RECORD_ROLES = 2
    LINKED_AGENT_EVENT_ROLES = 3
    NAME_SOURCE = 4
    NAME_RULE = 5
    ACCESSION_ACQUISITION_TYPE = 6
    ACCESSION_RESOURCE_TYPE = 7
    COLLECTION_MANAGEMENT_PROCESSING_PRIORITY = 8
    COLLECTION_MANAGEMENT_PROCESSING_STATUS = 9
    DATE_ERA = 10
    DATE_CALENDAR = 11
    DIGITAL_OBJECT_DIGITAL_OBJECT_TYPE = 12
    DIGITAL_OBJECT_LEVEL = 13
    EXTENT_EXTENT_TYPE = 14
    EVENT_EVENT_TYPE = 15
    CONTAINER_TYPE = 16
    AGENT_CONTACT_SALUTATION = 17
    EVENT_OUTCOME = 18
    RESOURCE_RESOURCE_TYPE = 19
    RESOURCE_FINDING_AID_DESCRIPTION_RULES = 20
    RESOURCE_FINDING_AID_STATUS = 21
    INSTANCE_INSTANCE_TYPE = 22
    SUBJECT_SOURCE = 23
    FILE_VERSION_USE_STATEMENT = 24
    FILE_VERSION_CHECKSUM_METHODS = 25
    LANGUAGE_ISO639_2 = 26
    LINKED_AGENT_ROLE = 27
    AGENT_RELATIONSHIP_ASSOCIATIVE_RELATOR = 28
    AGENT_RELATIONSHIP_EARLIERLATER_RELATOR = 29
    AGENT_RELATIONSHIP_PARENTCHILD_RELATOR = 30
    AGENT_RELATIONSHIP_SUBORDINATESUPERIOR_RELATOR = 31
    ARCHIVAL_RECORD_LEVEL = 32
    CONTAINER_LOCATION_STATUS = 33
    DATE_TYPE = 34
    DATE_LABEL = 35
    DATE_CERTAINTY = 36
    DEACCESSION_SCOPE = 37
    EXTENT_PORTION = 38
    FILE_VERSION_XLINK_ACTUATE_ATTRIBUTE = 39
    FILE_VERSION_XLINK_SHOW_ATTRIBUTE = 40
    FILE_VERSION_FILE_FORMAT_NAME = 41
    LOCATION_TEMPORARY = 42
    NAME_PERSON_NAME_ORDER = 43
    NOTE_DIGITAL_OBJECT_TYPE = 44
    NOTE_MULTIPART_TYPE = 45
    NOTE_ORDEREDLIST_ENUMERATION = 46
    NOTE_SINGLEPART_TYPE = 47
    NOTE_BIBLIOGRAPHY_TYPE = 48
    NOTE_INDEX_TYPE = 49
    NOTE_INDEX_ITEM_TYPE = 50
    COUNTRY_ISO_3166 = 51
    RIGHTS_STATEMENT_RIGHTS_TYPE = 52
    RIGHTS_STATEMENT_IP_STATUS = 53
    SUBJECT_TERM_TYPE = 54
    USER_DEFINED_ENUM_1 = 55
    USER_DEFINED_ENUM_2 = 56
    USER_DEFINED_ENUM_3 = 57
    USER_DEFINED_ENUM_4 = 58
    ACCESSION_PARTS_RELATOR = 59
    ACCESSION_PARTS_RELATOR_TYPE = 60
    ACCESSION_SIBLING_RELATOR = 61
    ACCESSION_SIBLING_RELATOR_TYPE = 62
    TELEPHONE_NUMBER_TYPE = 64
    RESTRICTION_TYPE = 65
    DIMENSION_UNITS = 66
    LOCATION_FUNCTION_TYPE = 67
    RIGHTS_STATEMENT_ACT_TYPE = 68
    RIGHTS_STATEMENT_ACT_RESTRICTION = 69
    NOTE_RIGHTS_STATEMENT_ACT_TYPE = 70
    NOTE_RIGHTS_STATEMENT_TYPE = 71
    RIGHTS_STATEMENT_EXTERNAL_DOCUMENT_IDENTIFIER_TYPE = 72
    RIGHTS_STATEMENT_OTHER_RIGHTS_BASIS = 73


class DataImportTypes(enum.Enum):
    """

    Specifies the default list of data import types available when creating a
    new data import job.

    """

    MARCXML_ACCESSION = "marcxml_accession"
    MARCXML = "marcxml"
    MARCXML_SUBJECTS_AND_AGENTS = "marcxml_subjects_and_agents"
    EAD_XML = "ead_xml"
    EAC_XML = "eac_xml"
    DIGITAL_OBJECT_CSV = "digital_object_csv"
    ASSESSMENT_CSV = "assessment_csv"
    ACCESSION_CSV = "accession_csv"
