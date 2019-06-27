import click

filter_opt = click.option(
    '-f',
    '--filter-by',
    type=click.Tuple([click.STRING, click.STRING]),
    default=(None, None),
    help='filter list by <field_name> <operator>,<value>',
)
sort_opt = click.option(
    '-s',
    '--sort',
    type=click.Tuple([click.STRING, click.STRING]),
    default=(None, None),
    help='sort by <field_name> <asc|desc>',
)

all_opt = click.option(
    '-a',
    '--show-all',
    is_flag=True,
    help='show all results',
    show_default=True,
)
count_opt = click.option(
    '-c', '--count', type=click.INT, help='size of results', default=50
)
page_opt = click.option(
    '-p', '--page', is_flag=True, help='page results in a less-like format'
)
