import os

GHERKAN_ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir, "data")
SUBJ_OF_INTEREST = "robot"

AND = "AND"
OR = "OR"
NOT = "NOT"
EQUALITY = "EQUALITY"
INEQUALITY = "INEQUALITY"
BOOL = "BOOL"
EDGE = "EDGE"
FORCE = "FORCE"
UNFORCE = "UNFORCE"

LBRACKET = "LBRACKET"
RBRACKET = "RBRACKET"
SKIP = "SKIP"
MISMATCH =  "MISMATCH"

LANG_CZ = "cs"
LANG_EN = "en"