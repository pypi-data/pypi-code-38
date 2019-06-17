# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


# TODO: Consume contracts from services common
PROP_EXISTS_FORMAT_STR = "(Properties/{0} ne null or Properties/{0} eq null)"
PROP_EQ_FORMAT_STR = "(Properties/{0} eq {1})"
TAG_EXISTS_FORMAT_STR = "(Tags/{0} ne null or Tags/{0} eq null)"
TAG_EQ_FORMAT_STR = "(Tags/{0} eq {1})"
STATUS_EQ_FORMAT_STR = "(Status eq {0})"
# TODO: Remove runsource filter after PuP
TYPE_EQ_FORMAT_STR = "(RunType eq {0} or Properties/azureml.runsource eq {0})"
CREATED_AFTER_FORMAT_STR = "(CreatedUtc ge {0})"
NO_CHILD_RUNS_QUERY = "(ParentRunId eq null)"

AND_OP = "and"
TARGET_EQ_FORMAT_STR = "(Target eq {0})"
