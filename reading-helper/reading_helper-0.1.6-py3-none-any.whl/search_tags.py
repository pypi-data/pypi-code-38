import re
from argparse import ArgumentParser
from pathlib import Path
from typing import Sequence
import pandas as pd


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "query",
        help="Boolean expression involving tags like `rl & (safe | symbolic)`. There must be spaces between tag names.",
    )
    parser.add_argument(
        "-d", "--dir", default=".", help="Papers directoy (default = '.'"
    )
    parser.add_argument("-p", "--print_path", action="store_true")
    args = parser.parse_args()
    return args


def search_tags(query: str, papers_dir: str = ".", print_path: bool = False) -> None:
    papers_dir = Path(papers_dir)
    papers = list(papers_dir.rglob("*.md"))

    remove_chars = "()|&~"
    query_tags = query
    for char in remove_chars:
        query_tags = query_tags.replace(char, "")
    # remove empty strings
    query_tags = list(filter(lambda tag: tag, query_tags.split(" ")))

    # {synonym: canonical form}
    tag_synonyms = {"safety": "safe", "human in the loop": "human-loop"}
    pattern = re.compile("tags: \[(.*?)\]", re.DOTALL)

    all_paper_tags = []
    for paper in papers:
        text = paper.read_text()
        match = pattern.search(text)
        if not match:
            print(f"{paper.stem} has no tags.")
            continue
        paper_tags = match.group(1).split(",")
        paper_tags = map(
            lambda t: t.lower().strip().replace('"', "").replace("'", ""), paper_tags
        )
        paper_tags = [tag_synonyms.get(tag, tag) for tag in paper_tags]
        tag_matches = [tag in paper_tags for tag in query_tags]
        all_paper_tags.append([paper] + tag_matches)

    tags_df = pd.DataFrame(all_paper_tags, columns=["paper"] + query_tags)
    for paper in tags_df.query(query).paper:
        if print_path:
            print(paper)
        else:
            print(paper.stem)


def main() -> None:
    args = parse_args()
    search_tags(args.query, args.dir, args.print_path)


if __name__ == "__main__":
    main()
