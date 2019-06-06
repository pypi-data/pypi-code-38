
DEFAULT_JOB_NAME = 'wf_job.ipynb'

PATTERNS_DIR = '.workflow_patterns_home'
RECIPES_DIR = '.workflow_recipes_home'
EXPORT_DIR = '.meow_export_home'

OBJECT_TYPE = 'object_type'
PERSISTENCE_ID = 'persistence_id'
TRIGGER = 'trigger'
TRIGGERS = 'triggers'
OWNER = 'owner'
NAME = 'name'
INPUT_FILE = 'input_file'
TRIGGER_PATHS = 'trigger_paths'
OUTPUT = 'output'
RECIPE = 'recipe'
RECIPES = 'recipes'
VARIABLES = 'variables'
VGRIDS = 'vgrids'

OUTPUT_MAGIC_CHAR = '*'

PLACEHOLDER = ''

VALID_PATTERN = {
    OBJECT_TYPE: str,
    PERSISTENCE_ID: str,
    TRIGGER: dict,
    OWNER: str,
    NAME: str,
    INPUT_FILE: str,
    TRIGGER_PATHS: list,
    OUTPUT: dict,
    RECIPES: list,
    VARIABLES: dict,
    VGRIDS: str
}

VALID_RECIPE = {
    OBJECT_TYPE: str,
    PERSISTENCE_ID: str,
    TRIGGERS: dict,
    OWNER: str,
    NAME: str,
    RECIPE: dict,
    VGRIDS: str
}

ANCESTORS = 'ancestors'
DESCENDENTS = 'descendents'

WORKFLOW_NODE = {
    ANCESTORS: {},
    DESCENDENTS: {}
}
