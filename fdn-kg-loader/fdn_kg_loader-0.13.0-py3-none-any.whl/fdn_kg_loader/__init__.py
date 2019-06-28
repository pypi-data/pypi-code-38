import click
import os
from fdn_kg_loader.model import Brand, Product, Category, CategoryTree, CategorizedRel, ProducedRel
from fdn_kg_loader.store import Store
from fdn_kg_loader.filter import *
from fdn_kg_loader.loader import *

KEYSPACE = 'schema_check'
# HOST = '35.240.223.141'
# 35.240.223.141
HOST = 'localhost'
CURDIR = os.path.dirname(os.path.abspath(__file__))
xstore = Store(keyspace=KEYSPACE, host=HOST)

@click.command()
def load_brand_cmd(base, pattern):
    fpath = os.path.join(CURDIR, 'shapeshift/brand-all.csv')
    df = pd.read_csv(fpath)

    df = load_file_chunk(base_path=base, path_pattern=pattern)
    df = filter_brand_entity(df)

    load_brand(df,xstore)

@click.command()
def load_product_cmd(base, pattern):
    fpath = os.path.join(CURDIR, 'shapeshift/product-all.csv')
    df = pd.read_csv(fpath)
    print(df.head)

    #significant part

    df = load_file_chunk(base_path=base, path_pattern=pattern)
    df = filter_product_entity(df)

    load_product(df,xstore)

@click.command()
def load_category_cmd(base, pattern):
    # fpath = os.path.join(CURDIR, 'shapeshift/categories-fdbr-to-graph.csv')
    # df = pd.read_csv(fpath)

    df = load_file_chunk(base_path=base, path_pattern=pattern)
    df = filter_category_entity(df)

    load_category(df,xstore=xstore)

@click.command()
def relate_category_product_cmd(base, pattern):
    # fpath = os.path.join(CURDIR, 'shapeshift/product-category-relation.csv')
    # df = pd.read_csv(fpath)

    df = load_file_chunk(base_path=base, path_pattern=pattern)
    df = filter_product_category_relation(df)
    relate_category_product(df, xstore=xstore)

@click.command()
def build_category_tree_cmd(base, pattern):
    # fpath = os.path.join(CURDIR, 'shapeshift/categories-fdbr-to-graph.csv')
    # df = pd.read_csv(fpath)

    df = load_file_chunk(base_path=base, path_pattern=pattern)
    df = filter_category_tree_relation(df)
    build_category_tree(df,xstore=xstore)

@click.command()
def relate_product_brand_cmd(base, pattern):
    # fpath = os.path.join(CURDIR, 'shapeshift/product-brand-relation.csv')
    # df2 = pd.read_csv(fpath)

    df2 = load_file_chunk(base_path=base, path_pattern = pattern)
    df2 = filter_product_brand_relation(df2)
    relate_product_brand(df2, xstore=xstore)
    

@click.group()
def cli():
    pass

def main():
    cli.add_command(load_brand_cmd)
    cli.add_command(load_product_cmd)
    cli.add_command(load_category_cmd)
    cli.add_command(relate_category_product_cmd)
    cli.add_command(relate_product_brand_cmd)
    cli.add_command(build_category_tree_cmd)

    cli()