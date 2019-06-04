import angreal

@angreal.command()
@angreal.option('--option',is_flag=True,help="Just showing what an option looks like. ")
def angreal_cmd(option):
    """
    This is the foo task.
    """

    return