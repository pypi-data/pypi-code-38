import os
import sys
import asyncio
import aiohttp
from lxml import html
from rarfile import RarFile
from io import BytesIO
from pprint import pprint


base_url = 'http://www.gks.ru/metod/XML-2019/'
compendium_link = base_url + 'XML_plan_2019.htm'


async def fetch_file(session, url):
    async with session.get(url, timeout=60*60) as response:
        file_content = await response.content.read()
        zipped_package = RarFile(BytesIO(file_content))
        xml_filename = [name for name in zipped_package.namelist()
                        if name.endswith('.xml')][0]
        xml_file = zipped_package.read(xml_filename)

        async with open(os.path.join(ROOT, 'compendium', xml_filename), 'wb') as handler:
            await handler.write(xml_file)

        return await response.text()


async def fetch_files(loop, root_url):
    connector = aiohttp.TCPConnector(limit=100)
    async with aiohttp.ClientSession(loop=loop, connector=connector) as session:
        async with session.get(root_url, timeout=60*60) as response:
            html_content = await response.text()
            content = html.fromstring(html_content)

        urls = [''.join((base_url, element[2]))
                for element in content.iterlinks()
                if '/XML/' in element[2]]

        await asyncio.gather(*[fetch_file(session, url) for url in urls])

    return urls


def get_files(url):
    loop = asyncio.get_event_loop()
    urls = loop.run_until_complete(fetch_files(loop, url))

    return urls


if __name__ == '__main__':
    try:
        ROOT = sys.argv[1]
        urls = get_files(compendium_link)
        pprint(urls)
        print(len(urls))
    except IndexError as ex:
        print(ex)
