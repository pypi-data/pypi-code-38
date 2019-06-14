'''
Preprocessor for Foliant documentation authoring tool.
Downloads design layout images from Sympli CDN
using certain Sympli account, resizes these images
and binds them with the documentation project.

Uses Node.js, headless Chrome, Puppeteer, wget, and external
script written in JavaScript. This script, as specified
in the installator, must be located in ``/usr/local/bin``
directory, must be added to ``PATH``, and must be executable.
These conditions may be overridden in the config.
'''

import re
from pathlib import Path
from hashlib import md5
from subprocess import run, PIPE, STDOUT, CalledProcessError
from time import sleep
from typing import Dict
OptionValue = int or float or bool or str

from foliant.utils import output
from foliant.preprocessors.base import BasePreprocessor


class Preprocessor(BasePreprocessor):
    defaults = {
        'get_sympli_img_urls_path': 'get_sympli_img_urls.js',
        'wget_path': 'wget',
        'convert_path': 'convert',
        'cache_dir': Path('.bindsymplicache'),
        'sympli_login': '',
        'sympli_password': '',
        'image_width': 800,
        'max_attempts': 5,
    }

    tags = 'sympli',

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._cache_dir_path = self.project_path / self.options['cache_dir']
        self._design_urls_file_path = self._cache_dir_path / 'design_urls.txt'
        self._img_urls_file_path = self._cache_dir_path / 'img_urls.txt'

        self._img_urls = {}

        self.logger = self.logger.getChild('bindsympli')

        self.logger.debug(f'Preprocessor inited: {self.__dict__}')

    def _get_img_hash(self, img_url: str, resized: bool) -> str:
        img_hash = md5(f'{img_url}'.encode())

        if resized:
            img_hash.update(f'{self.options["image_width"]}'.encode())

        return f'{img_hash.hexdigest()}'

    def _process_sympli(self, options: Dict[str, OptionValue]) -> str:
        img_url = self._img_urls[options.get("url", "")]

        if not img_url.startswith('https://cdn.sympli.io/'):
            return ''

        resized_img_path = self._cache_dir_path / f'resized_{self._get_img_hash(img_url, True)}.png'
        resized_img_ref = f'![{options.get("caption", "")}]({resized_img_path.absolute().as_posix()})'
        return resized_img_ref

    def process_sympli(self, markdown_content: str) -> str:
        def _sub(design_definition) -> str:
            return self._process_sympli(self.get_options(design_definition.group('options')))

        return self.pattern.sub(_sub, markdown_content)

    def apply(self):
        self.logger.info('Applying preprocessor')

        design_urls = []

        for markdown_file_path in self.working_dir.rglob('*.md'):
            with open(markdown_file_path, encoding='utf8') as markdown_file:
                markdown_content = markdown_file.read()

            design_definitions = re.finditer(self.pattern, markdown_content)

            for design_definition in design_definitions:
                design_url = self.get_options(design_definition.group('options')).get('url', '')

                if design_url not in design_urls:
                    design_urls.append(design_url)

        self.logger.debug(f'Design URLs: {design_urls}')

        if design_urls:
            self._cache_dir_path.mkdir(parents=True, exist_ok=True)

            if self._design_urls_file_path.exists():
                self._design_urls_file_path.unlink()

            with open(self._design_urls_file_path, 'w', encoding='utf8') as design_urls_file:
                design_urls_file.write("\n".join(design_urls) + "\n")

                self.logger.debug(f'Design URLs saved into the file: {self._design_urls_file_path}')

            output('Trying to run Puppeteer-based script', self.quiet)

            command = f'{self.options["get_sympli_img_urls_path"]} ' \
                      f'{self._cache_dir_path.absolute().as_posix()} ' \
                      f'{self.options["sympli_login"]} ' \
                      f'{self.options["sympli_password"]}'

            attempt = 0

            while True:
                attempt += 1

                try:
                    output(f'Attempt {attempt}', self.quiet)

                    self.logger.debug(f'Running Puppeteer-based script, attempt {attempt}')

                    command_output = run(command, shell=True, check=True, stdout=PIPE, stderr=STDOUT)

                    if command_output.stdout:
                        output(command_output.stdout.decode('utf8', errors='ignore'), self.quiet)

                except CalledProcessError as exception:
                    if attempt >= self.options["max_attempts"]:
                        self.logger.error(str(exception))

                        raise RuntimeError(f'Failed: {exception.output.decode()}')

                    else:
                        sleep(5 * attempt)
                        continue

                break

            with open(self._img_urls_file_path, encoding='utf8') as img_urls_file:
                for line in img_urls_file:
                    (design_url, img_url) = line.split()

                    self._img_urls[design_url] = img_url

                    if not img_url.startswith('https://cdn.sympli.io/'):
                        warning_message = f'Invalid image URL for the design page {design_url}: {img_url}'

                        if img_url == 'NOT_FOUND':
                            warning_message = f'Design {design_url} not found'

                        self.logger.warning(warning_message)

                        output(warning_message, self.quiet)

                        continue

                    original_img_path = self._cache_dir_path / f'original_{self._get_img_hash(img_url, False)}.png'

                    self.logger.debug(f'Original image path: {original_img_path}')

                    if not original_img_path.exists():
                        self.logger.debug('Original image not found in cache')

                        try:
                            self.logger.debug(f'Downloading original image: {img_url}')

                            command = f'{self.options["wget_path"]} ' \
                                      f'-O {original_img_path.absolute().as_posix()} ' \
                                      f'{img_url}'
                            run(command, shell=True, check=True, stdout=PIPE, stderr=STDOUT)

                        except CalledProcessError as exception:
                            self.logger.error(str(exception))

                            raise RuntimeError(f'Failed: {exception.output.decode()}')

                    resized_img_path = self._cache_dir_path / f'resized_{self._get_img_hash(img_url, True)}.png'

                    self.logger.debug(f'Resized image path: {resized_img_path}')

                    if not resized_img_path.exists():
                        self.logger.debug('Resized image not found in cache')

                        try:
                            self.logger.debug(f'Resizing original image, width: {self.options["image_width"]}')

                            command = f'{self.options["convert_path"]} ' \
                                      f'{original_img_path.absolute().as_posix()} ' \
                                      f'-resize {self.options["image_width"]} ' \
                                      f'{resized_img_path.absolute().as_posix()}'
                            run(command, shell=True, check=True, stdout=PIPE, stderr=STDOUT)

                        except CalledProcessError as exception:
                            self.logger.error(str(exception))

                            raise RuntimeError(f'Failed: {exception.output.decode()}')

            for markdown_file_path in self.working_dir.rglob('*.md'):
                with open(markdown_file_path, encoding='utf8') as markdown_file:
                    markdown_content = markdown_file.read()

                processed_content = self.process_sympli(markdown_content)

                if processed_content:
                    with open(markdown_file_path, 'w', encoding='utf8') as markdown_file:
                        markdown_file.write(processed_content)

        self.logger.info('Preprocessor applied')
