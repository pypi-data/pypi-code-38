import glob
from .extract import extract_markdown_links

markdown_files = glob.glob('**/*.md', recursive=True)
for url in extract_markdown_links(markdown_files):
    print(url)