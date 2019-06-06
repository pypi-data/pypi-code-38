# -*- coding: utf-8 -*-
import argparse


def create_indexing_argument_parser(choices):
    parser = argparse.ArgumentParser(description="Process some command line arguments.", prog="reindexes")
    parser.add_argument("--offset", type=int, help="starting point of indexing")
    parser.add_argument("--limit", type=int, help="endpoint of indexing")
    parser.add_argument("--index", type=str, choices=choices, help="catagory of objects to be indexed")
    parser.add_argument("--id", type=int, help="id of a given item to be indexed")
    return parser
