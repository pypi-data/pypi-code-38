#!/usr/bin/env python3
# encoding: utf-8

from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader("pylsar", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


def main():
    t_post = env.get_template("post.xml")
    print(t_post.render(param="toto"))
