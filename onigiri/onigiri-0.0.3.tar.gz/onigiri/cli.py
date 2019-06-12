# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET

import click

# Hack to enable Python2.7 to use encoding.
import sys
import warnings
if sys.version_info[0] < 3:
    import io
    import warnings
    open = io.open
    warnings.warn(str('You should really be using Python3!!! '
                      'Tick tock, tick tock, https://pythonclock.org/'))

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option()
def cli():
    pass

@cli.command('xml-extract')
@click.option('--language', '-l', required=True, help='Extract the language tags in the XML file.')
@click.option('--input', '-i', required=True, help='Path to the input XML file.')
@click.option('--output', '-o', default=None, help='Path to save the output .tsv file.')
@click.option('--encoding', '-e', default='utf8', help='Specify encoding of file.')
def xml_extract(language, input, output, encoding):
    # Read the XML file.
    tree = ET.parse(input)
    root = tree.getroot()
    # Set output filename.
    if output == None:
        output = input +'.tsv'
    with open(output, 'w', encoding=encoding) as fout:
        for term in root:
            term_idx = term.attrib['ID']
            term_str = next(ch for ch in term.getchildren()[0].getchildren() if ch.tag.endswith(language)).text
            if term_str:
                print(' '.join([term_idx, term_str]), end='\n', file=fout)


@cli.command('patch-xml-translations')
@click.option('--language', '-l', required=True, help='The language tag to patch in the XML file.')
@click.option('--input', '-i', required=True, help='Path to the input XML file.')
@click.option('--translations', '-t', default=None, help='Path to save the translated .tsv file.')
@click.option('--output', '-o', default=None, help='Path to save the output .tsv file.')
@click.option('--namespace', '-n', help='XML namespace.')
@click.option('--encoding', '-e', default='utf8', help='Specify encoding of file.')
def xml_extract(language, input, translations, output, namespace, encoding):
    # Read the XML file.
    ET.register_namespace("", namespace)
    tree = ET.parse(input)
    root = tree.getroot()
    # Read the translation file.
    idx2translation = {}
    with open(translations) as fin:
        for line in fin:
            idx, _, translation = line.strip().partition(' ')
            idx2translation[idx] = translation
    # Patch the XML
    for term in root:
        term_idx = term.attrib['ID']
        for ch in term.getchildren()[0].getchildren():
            if ch.tag.endswith(language) and term_idx in idx2translation:
                ch.text = idx2translation[term_idx]

    # Set output filename.
    if output == None:
        output = input +'.translated'
    tree.write(output, encoding="UTF-8",xml_declaration=True)
