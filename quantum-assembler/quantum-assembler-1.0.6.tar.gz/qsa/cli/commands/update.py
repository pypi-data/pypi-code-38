

def createparser(parent, commands):
    parent.set_defaults(func=main)


def main(assembler, logger):
    logger.debug("Compiling all enabled QSA extensions.")
    assembler.fullassemble()
