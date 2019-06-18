# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['slag']

package_data = \
{'': ['*'], 'slag': ['css/*', 'html/*']}

install_requires = \
['Jinja2>=2.10.1,<3.0.0',
 'Markdown>=3.1,<4.0',
 'Pygments>=2.4,<3.0',
 'attrs>=19.1,<20.0',
 'click>=7.0,<8.0',
 'pygit2==0.27.4',
 'toml>=0.10.0,<0.11.0']

entry_points = \
{'console_scripts': ['slag = slag:render_all']}

setup_kwargs = {
    'name': 'slag',
    'version': '0.4.0',
    'description': 'A distributed micro-blog social network on the blockchain.',
    'long_description': '# slag\n\nA fresh, static microblog system based on\n[modern block chain technologies](https://git-scm.com).\n\nSlag uses a list of Git repositories ("streams") to generate static HTML\nfiles. The targeted serving platform is\n[GitHub Pages](https://pages.github.com), but you can serve them however you\nwant. [Here](https://scizzorz.github.io) is an example slag\n(repository [here](https://github.com/scizzorz/scizzorz.github.io)).\n\n## Installation\n\n    pip install slag\n\n## Usage\n\n    slag [OPTIONS] [PATHS]...\n\n    Options:\n      -u, --baseurl TEXT           Base URL for all internal links\n      -t, --target TEXT            Directory to dump rendered HTML\n      -i, --include TEXT           Additional directories to include\n      -s, --pagesize INTEGER       Number of posts to display per page\n      -g, --maxparagraphs INTEGER  Number of preview paragraphs to display\n      -x, --hrefsuffix             Remove .html suffix from internal links\n      -d, --datefmt TEXT           Format to pass to strftime() for dates\n      -c, --config TEXT            Config file to load\n\nConfig files are specified in TOML. Any options specified on the command line\noverride the options specified in the config file. By default, a file named\n`slag.toml` is loaded as the config.\n\n## Streams\n\nEach source repository is used as a different "stream" of posts. Slag generates\na "post" from each commit in the stream repositories, except those that having\na leading `!` in their commit message. A chronologically descending list of\nposts is generated for each individual stream as well as a single combined list\nof all streams.\n\nEach post pulls its author, timestamp, URL slug, title, and body from the\ncommit information. The first line of the commit message is used as the post\ntitle, while the rest are used as the post body. Content is formatted using\n[Python Markdown](https://pypi.org/project/Markdown/). A number of paragraphs\n(specified by `--maxparagraphs`, defaults to `1`) are used as \'preview\'\nparagraphs in the list views.\n\n### Markdown Extensions\n\nSlag supports some "extensions" (I guess you can call them that?) to work\naround some of the features of Git that aren\'t super ideal\nin a blogging system.\n\n#### `!file` or `!code`\n\nIf a paragraph starts with `!file` or `!code` followed by a file path that\nexists in that commit\'s repository, Slag will expand the `!file` declaration\ninto a [syntax-highlighted](http://pygments.org) code block. Slag uses the\nversion of the file at its current `HEAD` rather than the version of the file\nin that commit. This works around Git\'s ~inability to edit the history~\nimmutable history feature.\n\n#### `!md`\n\nLike the `!file` extension, if a paragraph starts with `!md` and a file path,\nthe paragraph is expanded to the contents of the given file and then rendered as\nMarkdown. Again, Slag uses the version of the file at its current `HEAD`,\nenabling you edit posts without having to change your URLs. ~However, the act of\nediting a file will require a commit to the repository, which will then be used\nas a new post... so it\'s not a totally fool-proof workaround. Tough.~ Fixed:\ngive your edit commit a leading `!` and Slag will ignore it.\n\n## Motivation\n\nSlag started as a personal shitpost project but it actually doesn\'t seem\nterrible. Some features of Git are fairly amenable to use in a blog engine like\nthis, like me not having to write some database schema or clever file system\nlayout to generate content from. Plus, it\'s easy to pull on guest authors or\neven include someone else\'s content in your own slag by adding it as a\nsubmodule.  Neat.\n',
    'author': 'John Weachock',
    'author_email': 'jweachock@gmail.com',
    'url': 'https://github.com/scizzorz/slag',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
