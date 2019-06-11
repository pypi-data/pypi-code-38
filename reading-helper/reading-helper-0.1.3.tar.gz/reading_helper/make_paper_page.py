import requests
from datetime import datetime
from bs4 import BeautifulSoup
from argparse import ArgumentParser
from pathlib import Path
from typing import Dict, Optional


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("short_title", help="Short title for paper; used to name file.")
    parser.add_argument("-u", "--url", default="")
    parser.add_argument(
        "-j",
        "--journal",
        help="Journal published in [default = arXiv if 'arxiv' in url else '']",
        default="",
    )
    parser.add_argument(
        "-d",
        "--papers_dir",
        help="Directory where papers should be saved (default = current directory).",
    )
    return parser.parse_args()


def make_paper_page(short_title: str, url: str, journal: str, papers_dir: str = "."):
    journal = "arXiv" if "arxiv" in url and not journal else journal

    paper_data = {
        "url": url,
        "added_date": str(datetime.now().date()),
        "short_title": short_title,
        "journal": journal,
        "tags": "[]",
        "title": "",
        "authors": "[]",
        "year": "",
        "arxiv_id": "",
    }

    if "arxiv" in url:
        if "pdf" in url:
            url = url.replace(".pdf", "").replace("pdf", "abs")
        paper_data.update(extract_arxiv_data(url))
        paper_data["authors"] = (
            "[" + ", ".join(f'"{author}"' for author in paper_data["authors"]) + "]"
        )
    elif url:
        response = requests.get(url)
        html = BeautifulSoup(response.content, "lxml")

        try:
            paper_data.update({"title": str(html.select_one("h1").string)})
        except AttributeError:
            pass

    try:
        template = (Path(papers_dir) / "template.md").read_text()
    except FileNotFoundError:
        template = (Path(__file__).parents[1] / "template.md").read_text()
    template = template.format(**paper_data)

    new_paper_fname = short_title.lower().replace(" ", "_").replace("-", "_") + ".md"
    new_paper_path = (
        Path(papers_dir) / new_paper_fname if papers_dir else Path(new_paper_fname)
    )

    if new_paper_path.exists():
        overwrite = input(f"Overwrite existing file {new_paper_fname} (y/n)? ")
        if overwrite != "y":
            return

    new_paper_path.write_text(template)


def extract_arxiv_data(url: str) -> Dict[str, str]:
    paper_data = {}

    response = requests.get(url)

    html = BeautifulSoup(response.content, "lxml")
    meta_tags = html.select("meta")

    def filter_by_name(tags, name: str):
        return filter(lambda tag: tag.has_attr("name") and tag["name"] == name, tags)

    try:
        paper_data["title"] = next(filter_by_name(meta_tags, "citation_title"))[
            "content"
        ]
    except StopIteration:
        pass

    paper_data["authors"] = [
        tag["content"] for tag in filter_by_name(meta_tags, "citation_author")
    ]

    # format is YYYY/MM/DD (always?)
    # there's both a "citation_date" and a "citation_online_date"; I use "citation_date"
    try:
        paper_data["year"] = next(filter_by_name(meta_tags, "citation_date"))[
            "content"
        ].split("/")[0]
    except StopIteration:
        pass

    try:
        paper_data["arxiv_id"] = next(filter_by_name(meta_tags, "citation_arxiv_id"))[
            "content"
        ]
    except StopIteration:
        pass

    return paper_data


def main() -> None:
    args = parse_args()
    make_paper_page(args.short_title, args.url, args.journal, args.papers_dir)


if __name__ == "__main__":
    main()
