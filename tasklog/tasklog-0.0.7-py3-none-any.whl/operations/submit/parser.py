from pytimeparse import parse as parseDuration
from lark import Lark, Transformer
from .generictasklog import GenericWorklog


class WorklogTransformer(Transformer):
    def tasklog(self, tasklogProperties):
        (projectKey, issueKey) = tasklogProperties[0]

        (day, month, year) = tasklogProperties[1]
        # FIXME parse any date
        date = "{:s}-{:s}-{:s}".format(day, month, year)

        (timeDuration, timeUnit) = tasklogProperties[2]
        durationInSeconds = parseDuration("{:s}{:s}".format(timeDuration.strip(), timeUnit.strip()))

        description = tasklogProperties[3]

        if issueKey is not None:
            issueKey = "{:s}-{:s}".format(projectKey, issueKey)

        wk = GenericWorklog(projectKey, issueKey, date, durationInSeconds, description)

        return wk

    def jira_identifier(self, values):
        parts = values[0]
        count = len(parts)
        projectKey = None
        issueKey = None

        if count == 1:
            projectKey = parts[0]
        if count == 2:
            projectKey = parts[0]
            issueKey = parts[1]

        return (projectKey, issueKey)

    def jira_project_key(self, tokens):
        if len(tokens) >= 1:
            projectKeyToken = tokens[0]
            return [projectKeyToken.value]

        return None

    def jira_issue_key(self, tokens):
        if len(tokens) >= 2:
            projectKeyTokenAsString = tokens[0][0]
            partialIssueKeyToken = tokens[1]
            return [projectKeyTokenAsString, partialIssueKeyToken.value]

        return None

    def time_spent(self, tokens):
        count = len(tokens)

        if count == 0:
            return (None, None)

        if count == 1:
            durationToken = tokens[0]

        if count == 2:
            durationToken = tokens[0]
            durationUnitToken = tokens[1]

        return (durationToken.value, durationUnitToken.value)

    def time_unit(self, tokens):
        return tokens[0].value if len(tokens) == 1 else None

    def date(self, tokens):
        dayToken = tokens[0]
        monthToken = tokens[1]
        yearToken = tokens[2]

        return (dayToken.value, monthToken.value, yearToken.value)

    def description(self, tokens):
        val = "".join(tokens)

        return val


def parseGenericWorklog(rawWorkLog):
    # Sample raw import
    """

    #################################################
    # Sample Worklog
    #################################################

    # WORKLOG
    MYCOOLPROJECT
    25-12-2019
    8h
    This was fun and cool

    WORKLOG#
    Same as above
    """

    # Worklog Grammar Definition
    jiraWorklogGrammar = r"""
    tasklog: jira_identifier _WS* _NEWLINE+ date _WS* _NEWLINE+ time_spent _WS* _NEWLINE+ description?
    jira_identifier: jira_issue_key | jira_project_key
    jira_issue_key: jira_project_key "-" INT
    jira_project_key: (INT | WORD )+

    time_spent: (INT | DECIMAL) _WS* TIME_UNIT
    TIME_UNIT: "w" | "d" | "m" | "h" | "s"

    date: INT "-" INT "-" INT
    
    _WS : WS
    _NEWLINE : NEWLINE

    description: (/./)+

    // Defined at https://github.com/lark-parser/lark/blob/master/lark/grammars/common.lark
    
    %import common.WORD
    %import common.INT
    %import common.DECIMAL
    %import common.LETTER
    %import common.WS_INLINE
    %import common.NEWLINE
    %import common._STRING_INNER
    %import common.WS

    %ignore WS
    """

    # Build AST from text + grammar
    parser = Lark(jiraWorklogGrammar, start="tasklog", parser='earley', lexer='auto', debug=True)
    tree = parser.parse(rawWorkLog)
    print(tree.pretty())

    # Turn AST into Worklog object
    tasklog = WorklogTransformer().transform(tree)

    return tasklog
