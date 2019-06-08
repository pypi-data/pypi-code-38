from pathlib import Path
from ebooklib import epub

CSS_DIR = Path(__file__).parents[2] / 'css'


def make_css(name):
    return epub.EpubItem(
        uid=f'style_{name}',
        file_name=f'style/{name}.css',
        media_type='text/css',
        content=open(CSS_DIR / f'{name}.css').read(),
    )
