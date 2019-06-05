import argparse
import atexit
from collections import defaultdict
import importlib.resources
import os
import shutil
import subprocess
import sys
from tempfile import NamedTemporaryFile, TemporaryDirectory

from mdc import __version__ as mdc_version
import mdc.resources
import mdc.templates

__all__ = ["build_pandoc_cmd", "run_compile"]

DEFAULT_FROM = "markdown-markdown_in_html_blocks-native_divs"
AVAILABLE_TEMPLATES = [
    "icml",
    "neurips",
    "note",
    "simple",
    "standalone",
    "stylish",
]
DEFAULT_TEMPLATE = "simple"
TEMPLATE_RESOURCES = defaultdict(
    list,
    {
        "icml": ["icml.bst", "icml.sty"],
        "neurips": ["neurips.sty"],
        "simple": [
            "ebgaramond12-regular.otf",
            "ebgaramond12-italic.otf",
            "ebgaramondcaps12-regular.otf",
            "lmmono10-regular.otf",
            "lmmono10-italic.otf",
            "lmmonocaps10-regular.otf",
        ],
        "stylish": [
            "ebgaramond12-regular.otf",
            "ebgaramond12-italic.otf",
            "ebgaramondcaps12-regular.otf",
            "futurabook-regular.ttf",
            "futurabook-italic.ttf",
            "futuramedium-regular.ttf",
            "lmmono10-regular.otf",
            "lmmono10-italic.otf",
            "lmmonocaps10-regular.otf",
        ],
    },
)
DEFAULT_BIBTYPE = "natbib"
DEFAULT_META = [
    "figPrefix=Figure",
    "eqnPrefix=Equation",
    "tblPrefix=Table",
    "lstPrefix=List",
    "secPrefix=Section",
]
DEFAULT_PANDOC = "pandoc"
DEFAULT_LATEXMK = "latexmk"
DEFAULT_CROSSREF = "pandoc-crossref"
DEFAULT_IMG_EXT = "pdf"
DEFAULT_VERBOSE = False


def build_pandoc_cmd(
    input_file,
    from_=DEFAULT_FROM,
    template=DEFAULT_TEMPLATE,
    bibliography=None,
    bib_type=DEFAULT_BIBTYPE,
    crossref=DEFAULT_CROSSREF,
    include=None,
    meta=DEFAULT_META,
    pandoc=DEFAULT_PANDOC,
):
    """Build required pandoc command from given arguments."""
    cmd = [pandoc]

    cmd.append(f"--from={from_}")
    cmd.append("--to=latex")

    if template in AVAILABLE_TEMPLATES:
        template_context = importlib.resources.path(
            mdc.templates, f"{template}.tex"
        )
        template = template_context.__enter__()
        atexit.register(
            lambda c: c.__exit__(None, None, None), template_context
        )
    cmd.append(f"--template={template}")

    if bibliography is not None:
        cmd.append(f"--bibliography={bibliography}")
        cmd.append(f"--{bib_type}")

    if crossref is not None:
        cmd.append(f"--filter={crossref}")

    if include:
        for f in include:
            cmd.append(f"--include-before-body={f}")

    if meta:
        for m in meta:
            cmd.append(f"--metadata={m}")

    cmd.append(f"--default-image-extension={DEFAULT_IMG_EXT}")

    cmd.append(input_file)
    return cmd


def run_compile(
    pandoc_cmd,
    template,
    output_file=None,
    latexmk=DEFAULT_LATEXMK,
    verbose=DEFAULT_VERBOSE,
):
    """Run pandoc command to generate tex/pdf output."""
    if TEMPLATE_RESOURCES[template]:
        # Create and populate resources directory
        if not os.path.exists("resources"):
            os.mkdir("resources")
        for resc in TEMPLATE_RESOURCES[template]:
            if not os.path.exists(os.path.join("resources", resc)):
                with importlib.resources.path(mdc.resources, resc) as resc_path:
                    shutil.copyfile(resc_path, os.path.join("resources", resc))

    if output_file is None:
        subprocess.run(pandoc_cmd).check_returncode()
    elif output_file.endswith(".tex"):
        pandoc_cmd.append(f"--output={output_file}")
        subprocess.run(pandoc_cmd).check_returncode()
    elif output_file.endswith(".pdf"):
        # Generate tex, then compile with latexmk
        with NamedTemporaryFile(dir="") as temp_file:
            pandoc_cmd.append(f"--output={temp_file.name}")
            subprocess.run(pandoc_cmd).check_returncode()

            with TemporaryDirectory() as temp_dir:
                latexmk_cmd = [
                    latexmk,
                    "-pdf",
                    "-lualatex",
                    f"-output-directory={temp_dir}",
                    f"{temp_file.name}",
                ]
                if not verbose:
                    latexmk_cmd.append("-quiet")
                subprocess.run(latexmk_cmd).check_returncode()

                # Copy generated output file
                tf_only_name = os.path.basename(temp_file.name)
                shutil.copyfile(
                    os.path.join(temp_dir, f"{tf_only_name}.pdf"),
                    f"{output_file}",
                )
    else:
        raise ValueError("output file extension must be .tex/.pdf")


def main():
    """Entry point."""

    def _meta_arg(string):
        """Argument type for passing meta variables."""
        if "=" not in string:
            raise argparse.ArgumentTypeError(
                "meta var should be passed as " "`key=val`"
            )
        k, v = string.split("=")
        return f"{k}:{v}"

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("input_file", type=argparse.FileType("r"))
    arg_parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {mdc_version}"
    )
    arg_parser.add_argument(
        "-v", "--verbose", action="store_true", help="make latexmk verbose"
    )
    arg_parser.add_argument(
        "-o",
        "--output-file",
        type=str,
        default=None,
        help="write output to this file (default stdout)",
    )
    arg_parser.add_argument(
        "-f",
        "--from",
        type=str,
        dest="from_",
        metavar="FROM",
        default=DEFAULT_FROM,
        help=f"pandoc input format (default {DEFAULT_FROM})",
    )
    template_parser = arg_parser.add_mutually_exclusive_group(required=False)
    template_parser.add_argument(
        "-t",
        "--builtin-template",
        type=str,
        dest="template",
        choices=AVAILABLE_TEMPLATES,
        help=f"use one of the built-in templates (default {DEFAULT_TEMPLATE})",
    )
    template_parser.add_argument(
        "-T",
        "--custom-template",
        type=str,
        dest="template",
        metavar="CUSTOM_TEMPLATE",
        help="use a custom template",
    )
    arg_parser.set_defaults(template=DEFAULT_TEMPLATE)
    arg_parser.add_argument(
        "-b",
        "--bibliography",
        type=argparse.FileType("r"),
        default=None,
        help="bibliography argument for pandoc",
    )
    arg_parser.add_argument(
        "-B",
        "--bib-type",
        type=str,
        choices=["natbib", "biblatex"],
        default=DEFAULT_BIBTYPE,
        help=f"bibliography type sent to pandoc (default {DEFAULT_BIBTYPE})",
    )
    arg_parser.add_argument(
        "-i",
        "--include",
        type=argparse.FileType("r"),
        nargs="*",
        help="files to include before body",
    )
    arg_parser.add_argument(
        "-m",
        "--meta",
        type=_meta_arg,
        nargs="*",
        default=DEFAULT_META,
        help="additional meta variables to pass to pandoc",
    )
    arg_parser.add_argument(
        "--pandoc",
        type=str,
        default=DEFAULT_PANDOC,
        help=f"path to pandoc executable (default {DEFAULT_PANDOC})",
    )
    arg_parser.add_argument(
        "--latexmk",
        type=str,
        default=DEFAULT_LATEXMK,
        help=f"path to latexmk executable (default {DEFAULT_LATEXMK})",
    )
    arg_parser.add_argument(
        "--crossref",
        type=str,
        default=DEFAULT_CROSSREF,
        help=f"path to crossref executable (default {DEFAULT_CROSSREF})",
    )
    args = arg_parser.parse_args()

    try:
        pandoc_cmd = build_pandoc_cmd(
            args.input_file.name,
            args.from_,
            args.template,
            args.bibliography.name if args.bibliography is not None else None,
            args.bib_type,
            args.crossref,
            [i.name for i in args.include] if args.include is not None else [],
            args.meta,
            args.pandoc,
        )
        run_compile(
            pandoc_cmd,
            args.template,
            args.output_file,
            args.latexmk,
            args.verbose,
        )
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {e.cmd[0]} failed with return code {e.returncode}")
        return e.returncode
