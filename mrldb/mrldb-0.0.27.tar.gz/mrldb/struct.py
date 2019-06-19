__doc__=f"""mrldb by Rémi "Mr e-RL" LANGDORPH
Copyright (c) 2019 Rémi LANGDORPH - mrerl@warlegend.net
under MIT License (https://github.com/merlleu/mrldb/blob/master/LICENSE)"""
def get_struct_init(structure):
    return [
    "CREATE TABLE IF NOT EXISTS "+table+"("+", ".join(
    [
    colname+" "+content for colname, content in cols.items()
    ])+")"
    for table, cols in structure.items()
    ]
