from pathlib import Path

import click

from tree_html import DEFAULT_DESCRIPTION, color_scheme_dict
from tree_html.build_input import filter_tree_depth, generate_json_tree
from tree_html.parse import parse_links, parse_tree
from tree_html.render_assets import render_template, copy_static_assets
from tree_html.utils import remove_temp_files


@click.command()
@click.argument("target-dir", type=click.Path(exists=True, file_okay=False))
@click.argument("out-dir", type=click.Path(exists=True, writable=True), default=".")
@click.option(
    "-c",
    "--color-scheme",
    type=click.Choice(color_scheme_dict.keys()),
    default="grey",
    help="Color scheme to apply to HTML output",
)
@click.option(
    "-i",
    "--input-json",
    type=click.Path(exists=True, dir_okay=False),
    help="JSON file from `tree -J` to use as input instead of running tree internally",
)
@click.option(
    "-l",
    "--level",
    type=int,
    help="Levels of depth to traverse from the target directory (akin to '-L' in tree)",
)
@click.option(
    "-n",
    "--parent-name",
    help="Name to use as the top-level directory in the output instead of <TARGET_DIR>"
    "(may be useful for replacing '.' as the name used at the top-level)",
)
@click.option(
    "-d",
    "--description",
    type=str,
    default=DEFAULT_DESCRIPTION,
    help="Descriptive text to place below the heading of the output document",
)
@click.option(
    "-t",
    "--title",
    type=str,
    default="Directory tree",
    help="Title to use as the heading of the output document",
)
@click.option(
    "-e",
    "--external-link",
    type=str,
    multiple=True,
    help="Optional link and description to be included in output file, in the format: "
    "'link description'. This option can be supplied multiple times. Example: \n"
    "$> tree-html . -e 'www.google.com Click this resource for more information'",
)
def main(
    target_dir,
    out_dir,
    color_scheme,
    description,
    input_json,
    level,
    parent_name,
    title,
    external_link,
):
    """Renders a styled, interactive directory structure for TARGET_DIR
    and saves it as a single HTML file in OUT_DIR for ease of use.
    """
    if not input_json:
        input_json = generate_json_tree(target_dir, level)
        tree, top_level = parse_tree(input_json)
        remove_temp_files(input_json)
    else:
        tree, top_level = parse_tree(input_json)

    if parent_name:
        top_level = parent_name

    if description == DEFAULT_DESCRIPTION:
        description = description.replace("<TARGET_DIR|PARENT_NAME>", top_level)

    if level:
        tree = filter_tree_depth(level=level, tree=tree)

    external_links = parse_links(external_link)

    params = {
        "tree": tree,
        "external_links": external_links,
        "title": title,
        "description": description,
        "top_level": top_level,
    }

    output_path = Path(out_dir) / "tree-html-output"
    copy_static_assets(output_path, color_scheme)

    html_path = output_path / "rendered-tree-diagram.html"
    html_path.write_text(render_template("index.html", params=params))
