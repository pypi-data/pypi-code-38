"""Frontmatter module."""
import re

from ruamel.yaml import YAML

MARKUPS = {
    "YAML": re.compile(rb"(?:^---\s*\n)([\s\S]+?)(?:^(?:---|\.\.\.)\s*\n)", re.MULTILINE)}

PARSERS = {"YAML": YAML().load}


def parse(body):
    text = body.strip(b"\n")
    lang = None

    lang = select_language(text)
    if lang is None:
        return {}, text

    __, frontmatter, body = MARKUPS[lang].split(text, 2)
    frontmatter = frontmatter.strip(b"\n")
    body = body.strip(b"\n")

    frontmatter = PARSERS[lang](frontmatter)

    return frontmatter, body


def select_language(text):
    for lang, regex in MARKUPS.items():
        if regex.match(text):
            return lang
