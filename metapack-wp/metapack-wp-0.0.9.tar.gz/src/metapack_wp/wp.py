# Copyright (c) 2019 Civic Knowledge. This file is licensed under the terms of the
# MIT License, included in this distribution as LICENSE

"""
CLI program for managing packages
"""

import json
from os.path import basename
from textwrap import dedent
from uuid import uuid4

import yaml
from metapack import Downloader
from metapack.cli.core import (MetapackCliMemo, err, warn, get_config, prt)
from metapack.html import display_context
from metapack.util import ensure_dir
from metapack_build.build import find_csv_packages
from metapack_jupyter.wordpress import convert_wordpress
from rowgenerators import parse_app_url

downloader = Downloader.get_instance()


def wp(subparsers):
    parser = subparsers.add_parser(
        'wp',
        help='Publish a Jupyter notebook or data package to Wordpress ',
        description="""
        Write a notebook or package to Wordpress.

        If the source argument is a data package, package information will be submitted to the Wordpress blog as a
        blog post, formatted impliarly to the package html documentation file.

        If the source argument is a Jupyter notebook, the notebook is written as a blog post. See
        http://insights.civicknowledge.com for examples.

        """,
        epilog='Cache dir: {}\n'.format(str(downloader.cache.getsyspath('/'))))

    parser.set_defaults(run_command=run_wp)

    parser.add_argument('-g', '--group', nargs='?', action='append', help="Assign an additional group. Can be used "
                                                                          "multiple times, one onece with values "
                                                                          "seperated by commas")

    parser.add_argument('-t', '--tag', nargs='?', action='append', help="Assign an additional tag. Can be used "
                                                                        "multiple timesm or once with values "
                                                                        "seperated by commas")

    parser.add_argument('-H', '--header', help='Dump YAML of notebook header', action='store_true')

    parser.add_argument('-G', '--get', help='Get and dump the post, rather that update it', action='store_true')

    parser.add_argument('-P', '--profile', help="Name of a BOTO or AWS credentails profile", required=False)

    parser.add_argument('-p', '--publish', help='Set the post state to published, rather than draft',
                        action='store_true')

    parser.add_argument('-d', '--dump', help="Dump the HTML. Default if site_name is not specified",
                        action='store_true')


    parser.add_argument('-s', '--site_name', help="Site name, in the .metapack.yaml configuration file")

    parser.add_argument('-T', '--template', help="Name of Jinja2 template", default='wordpress.html')

    parser.add_argument('source', help="Path to a notebook file or a Metapack package")


def split_groups_tags(v):
    if not v:
        return

    for g in v:
        if ',' in g:
            for g_ in g.split(','):
                yield g_
        else:
            yield g


def run_wp(args):
    u = parse_app_url(args.source)

    if u.target_format == 'ipynb':
        run_notebook(args)
    else:

        args.metatabfile = args.source
        m = MetapackCliMemo(args, downloader)

        if args.dump or not args.site_name:
            doc, content = get_doc_content(m)
            print(content)
        elif args.site_name:
            run_package(m)


def run_notebook(args):
    p = '/tmp/metapack-wp-notebook/'
    ensure_dir(p)

    output_file, resources = convert_wordpress(args.source, p)

    r, post = publish_wp(args.site_name, output_file, resources, args)
    prt("Post url: ", post.link)


def get_site_config(site_name):
    config = get_config()

    if config is None:
        err("No metatab configuration found. Can't get Wordpress credentials. Maybe create '~/.metapack.yaml'")

    site_config = config.get('wordpress', {}).get(site_name, {})

    if not site_config:
        err("In config file '{}', expected 'wordpress.{}' section for site config"
            .format(config['_loaded_from'], site_name))

    if 'url' not in site_config or 'user' not in site_config or 'password' not in site_config:
        err(dedent(
            """
            Incomplete configuration. Expected:
                wordpress.{site_name}.url
                wordpress.{site_name}.user
                wordpress.{site_name}.password
            In configuration file '{cfg_file}'
            """.format(site_name=site_name, cfg_file=config['_loaded_from'])
        ))

    return site_config['url'], site_config['user'], site_config['password']


def prepare_image(slug, file_name, post_id):
    from xmlrpc import client as xmlrpc_client

    # prepare metadata
    data = {
        'name': 'picture.jpg',
        'type': 'image/jpeg',  # mimetype
    }

    # read the binary file and let the XMLRPC library encode it into base64
    with open(file_name, 'rb') as img:
        return {
            'name': '{}-{}'.format(slug, basename(file_name)),
            'type': 'image/png',  # mimetype
            'bits': xmlrpc_client.Binary(img.read()),
            'post_id': post_id
        }


def cust_field_dict(post):
    try:
        return dict((e['key'], e['value']) for e in post.custom_fields)
    except (KeyError, AttributeError):
        return {}


def find_post(wp, identifier):
    from wordpress_xmlrpc.methods.posts import GetPosts

    for _post in wp.call(GetPosts()):
        if cust_field_dict(_post).get('identifier') == identifier:
            return _post

    return None


def set_custom_field(post, key, value):
    if not hasattr(post, 'custom_fields') or not key in [e['key'] for e in post.custom_fields]:

        if not hasattr(post, 'custom_fields'):
            post.custom_fields = []

        post.custom_fields.append( {'key': key, 'value': value})


def publish_wp(site_name, output_file, resources, args):
    """Publish a notebook to a wordpress post, using Gutenberg blocks.

    Here is what the metadata looks like, in a section of the notebook tagged 'frontmatter'

    show_input: hide
    github: https://github.com/sandiegodata/notebooks/blob/master/tutorial/American%20Community%20Survey.ipynb
    identifier: 5c987397-a954-46ca-8743-bdcd7a71579c
    featured_image: 171
    authors:
    - email: eric@civicknowledge.com
      name: Eric Busboom
      organization: Civic Knowledge
      type: wrangler
    tags:
    - Tag1
    - Tag2
    categories:
    - Demographics
    - Tutorial

    'Featured_image' is an attachment id

    """

    from wordpress_xmlrpc import Client, WordPressPost
    from wordpress_xmlrpc.methods.media import UploadFile, GetMediaLibrary
    from wordpress_xmlrpc.methods.posts import NewPost, EditPost, GetPost

    # http://busboom.org/wptest/wp-content/uploads/sites/7/2017/11/output_16_0-300x200.png

    url, user, password = get_site_config(site_name)

    meta = {}
    for r in resources:
        if r.endswith('.json'):
            with open(r) as f:
                meta = json.load(f)

    fm = meta.get('frontmatter', {})

    if not 'identifier' in fm or not fm['identifier']:
        err("Can't publish notebook without a unique identifier. Add this to the "
            "Metatab document or frontmatter metadata:\n   identifier: {}".format(str(uuid4())))

    wp = Client(url, user, password)

    post = find_post(wp, fm['identifier'])

    if post:
        prt("Updating old post")
    else:
        post = WordPressPost()
        post.id = wp.call(NewPost(post))
        prt("Creating new post")

    post.title = fm.get('title', '')
    post.slug = fm.get('slug')

    with open(output_file) as f:
        content = f.read()

    post.terms_names = {
        'post_tag': fm.get('tags', []),
        'category': fm.get('categories', [])
    }

    if args.header:
        print(yaml.dump(fm, default_flow_style=False))

    set_custom_field(post, 'identifier', fm['identifier'])

    post.excerpt = fm.get('excerpt', fm.get('brief', fm.get('description')))

    def strip_image_name(n):
        """Strip off the version number from the media file"""
        from os.path import splitext
        import re
        return re.sub(r'\-\d+$', '', splitext(n)[0])

    extant_files = list(wp.call(GetMediaLibrary(dict(parent_id=post.id))))

    def find_extant_image(image_name):
        for img in extant_files:
            if strip_image_name(basename(img.metadata['file'])) == strip_image_name(image_name):
                return img

        return None

    for r in resources:

        image_data = prepare_image(fm['identifier'], r, post.id)
        img_from = "/{}/{}".format(fm['slug'], basename(r))

        extant_image = find_extant_image(image_data['name'])

        if extant_image:
            prt("Post already has image:", extant_image.id, extant_image.link)
            img_to = extant_image.link

        elif r.endswith('.png'):  # Foolishly assuming all images are PNGs
            response = wp.call(UploadFile(image_data, overwrite=True))

            prt("Uploaded image {} to id={}, {}".format(basename(r), response['id'], response['link']))

            img_to = response['link']

        content = content.replace(img_from, img_to)

    if fm.get('featured_image') and fm.get('featured_image').strip():
        post.thumbnail = int(fm['featured_image'])
    elif hasattr(post, 'thumbnail') and isinstance(post.thumbnail, dict):
        # The thumbnail expects an attachment id on EditPost, but returns a dict on GetPost
        post.thumbnail = post.thumbnail['attachment_id']

    post.content = content

    r = wp.call(EditPost(post.id, post))

    return r, wp.call(GetPost(post.id))


def html(doc, template):
    from markdown import markdown as convert_markdown
    from bs4 import BeautifulSoup
    from jinja2 import Environment, PackageLoader

    context = display_context(doc)

    if 'inline_doc' in context:
        extensions = [
            'markdown.extensions.extra',
            'markdown.extensions.admonition'
        ]

        inline_doc = convert_markdown(context['inline_doc'], extensions)

        idp = []

        tag_map = {
            'p': 'wp:paragraph',
            'ul': 'wp:list',
            'pre': 'wp:code',
            'h1': 'wp:heading',
            'h2': 'wp:heading',
            'h3': 'wp:heading',
            'h4': 'wp:heading',
            'h5': 'wp:heading',
            'h6': 'wp:heading',
        }

        nodes = BeautifulSoup(inline_doc, features="html.parser").find_all(recursive=False)

        context['inline_doc_parts'] = \
            [(tag_map.get(n.name, 'wp:html'), str(n)) for n in nodes]

    else:
        context['inline_doc_parts'] = []

    env = Environment(
        loader=PackageLoader('metapack_wp', 'support/templates')
        # autoescape=select_autoescape(['html', 'xml'])
    )

    return env.get_template(template).render(**context)


def get_doc_content(m):

    if not m.doc.find('Root.Distribution'):

        doc = find_csv_packages(m, downloader)
        if not doc:
            warn('Package has no Root.Distribution, and no CSV package found')
            doc = m.doc
        else:
            prt("Package has no Root.Distribution, using CSV package: ", doc.ref)
    else:
        doc = m.doc

    return doc, html(doc, m.args.template)


def run_package(m):
    """Publish documentation for a package as a post"""
    from wordpress_xmlrpc import Client, WordPressPost
    from xmlrpc.client import Fault
    from wordpress_xmlrpc.methods.posts import NewPost, EditPost
    from slugify import slugify


    doc, content = get_doc_content(m)

    url, user, password = get_site_config(m.args.site_name)
    wp = Client(url, user, password)

    post = find_post(wp, doc.identifier)

    if m.args.get:
        if post:
            post.content = "<content elided>"
            from pprint import pprint
            pprint(post.struct)
            return
        else:
            warn(f"Didn't find post for identifier {doc.identifier}")
            return

    if post:
        prt("Updating old post")
        action = lambda post: EditPost(post.id, post)
    else:
        prt("Creating new post")
        action = lambda post: NewPost(post)
        post = WordPressPost()

    set_custom_field(post, 'identifier', doc.identifier)
    set_custom_field(post, 'name', doc.name)
    set_custom_field(post, 'nvname', doc.nonver_name)

    post.excerpt = doc['Root'].get_value('Root.Description') or content[:200]

    post_tags = list(set(
        [t.value for t in doc['Root'].find('Root.Tag')] +
        [t.value for t in doc['Root'].find('Root.Group')] +
        [doc['Root'].get_value('Root.Origin')] +
        list(split_groups_tags(m.args.group)) +
        list(split_groups_tags(m.args.tag))
    ))

    post.terms_names = {
        'post_tag': post_tags,
        'category': ['Dataset'] + list(split_groups_tags(m.args.group))
    }

    post.title = doc.get_value('Root.Title')
    post.slug = slugify(doc.nonver_name)
    post.content = content

    if m.args.publish:
        post.post_status = 'publish'

    try:
        r = wp.call(action(post))
    except Fault as e:

        if 'taxonomies' in e.faultString:
            err(("User {} does not have permissions to add terms to taxonomies. "
                 "Terms are: {}").format(user, post.terms_names))

        raise

    return r
