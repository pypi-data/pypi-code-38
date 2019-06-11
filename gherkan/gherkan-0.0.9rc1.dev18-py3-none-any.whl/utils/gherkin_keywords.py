from gherkan.utils import constants as c

FEATURE = "Feature"
BACKGROUND = "Background"
SCENARIO = "Scenario"
GIVEN = "Given"
WHEN = "When"
THEN = "Then"
AND = "And"


FEATURE_CS = "Požadavek"
BACKGROUND_CS = "Kontext"
SCENARIO_CS = "Scénář"
GIVEN_CS = "Pokud"
WHEN_CS = "Když"
THEN_CS = "Pak"
AND_CS = "A"

KEYWORDS_EN = {
    "feature": FEATURE,
    "background": BACKGROUND,
    "scenario": SCENARIO,
    "given": GIVEN,
    "when": WHEN,
    "then": THEN,
    "and": AND,
}

KEYWORDS_CS = {
    "feature": FEATURE_CS,
    "background": BACKGROUND_CS,
    "scenario": SCENARIO_CS,
    "given": GIVEN_CS,
    "when": WHEN_CS,
    "then": THEN_CS,
    "and": AND_CS,
}

def get_kw(lang : str, key : str):
    if lang == c.LANG_EN:
        return KEYWORDS_EN[key.lower()]
    elif lang == c.LANG_CZ:
        return  KEYWORDS_CS[key.lower()]
    else:
        raise ValueError(f"Language not recognized: {lang}")