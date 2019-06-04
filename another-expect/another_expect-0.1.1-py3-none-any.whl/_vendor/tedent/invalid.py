from textwrap import dedent

expectedUsage = """
    Expected usage:
    tedent(f\"\"\"
        Some string
        {here}
    \"\"\")
    """

invalidFewerThan3Lines = dedent(
    f"""
    tedent expects a string with three or more lines.  When fewer are passed
    then they must contain only whitespace for this error not to be thrown.
    {expectedUsage}
    """
)

invalidFirstOrLastLine = dedent(
    f"""
    The first and last lines are only allowed to contain whitespace
    {expectedUsage}
    """
)

invalidSecondLine = dedent(
    f"""
    The second line must have a non-whitespace character
    {expectedUsage}
    """
)
