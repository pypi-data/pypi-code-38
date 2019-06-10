


def print_mutation_warning():
    msg = (
        "WARNING: Make sure that your repository branch is\n"
        "up-to-date with the remote. The storage format of\n"
        "the vaults can not be merged by Git. This means\n"
        "that merge conflicts are unresolvable.\n\n"
        "Merge this branch as quickly as possible into the\n"
        "mainline branch and instruct the other developers\n"
        "to update their local branches.\n\n"
        "Type \"yes\" to continue: "
    )
    if input(msg) != 'yes':
        print("You did not type \"yes\", aborting.")
        raise SystemExit
