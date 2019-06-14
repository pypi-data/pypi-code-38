from bs4 import BeautifulSoup
from bs4.element import Comment
from tld import get_tld
from urllib.parse import parse_qs
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.parse import urlsplit
import ipaddress
import logging
import magic
import re
import urllib
import warnings

warnings.filterwarnings('ignore', category=UserWarning, module='bs4')


def _tokenize(bytes, mimetype, extra_tokens=True):
    """ This function tokenizes the input bytes based on some common characters. It returns
        the tokens in ASCII format. """

    # Start with only the ASCII bytes. Limit it to 8+ character strings.
    try:
        ascii_bytes = b' '.join(re.compile(b'[\x00\x09\x0A\x0D\x20-\x7E]{8,}').findall(bytes))
        ascii_bytes = ascii_bytes.replace(b'\x00', b'')
    except:
        return []

    tokens = []

    # Find anything sandwiched between ( )
    results = re.compile(b'\(([^\)]+)\)').findall(ascii_bytes)
    #results = re.compile(b'\(([^\(\)]+)\)').findall(ascii_bytes)
    tokens += results

    # Find anything sandwiched between < >
    results = re.compile(b'\<([^\>]+)\>').findall(ascii_bytes)
    #results = re.compile(b'\<([^\<\>]+)\>').findall(ascii_bytes)
    tokens += results

    # Find anything sandwiched between [ ]
    results = re.compile(b'\[([^\]]+)\]').findall(ascii_bytes)
    #results = re.compile(b'\[([^\[\]]+)\]').findall(ascii_bytes)
    tokens += results

    # Find anything sandwiched between { }
    results = re.compile(b'\{([^\}]+)\}').findall(ascii_bytes)
    #results = re.compile(b'\{([^\{\}]+)\}').findall(ascii_bytes)
    tokens += results

    if not mimetype == 'data':

        # Find anything sandwiched between ' '
        results = re.compile(b'\'\s*(.*?)\s*\'').findall(ascii_bytes)
        tokens += results

        # Find anything sandwiched between " "
        results = re.compile(b'\"\s*(.*?)\s*\"').findall(ascii_bytes)
        tokens += results

    # Find anything sandwiched between spaces
    results = re.compile(b'\ ([^\ ]+)\ ').findall(ascii_bytes)
    tokens += results

    # Break the bytes apart if we want to generate even more tokens.
    if extra_tokens:

        # Add each newline as a token.
        lines = ascii_bytes.decode('ascii', errors='ignore').splitlines()
        tokens += [l.encode('ascii') for l in lines]

        # Now replace these characters in the ASCII bytes with spaces to create more tokens.
        replace_these = [b'(', b')', b'<', b'>', b'[', b']', b'{', b'}', b"'", b'"', b'\n', b'\r', b'\t', b'\\', b'`', b';']
        for char in replace_these:
            ascii_bytes = ascii_bytes.replace(char, b' ')

        # Split the bytes on spaces and use the results as tokens.
        tokens += ascii_bytes.split(b' ')

    # Decode the tokens as ASCII.
    tokens = [token.decode('ascii', errors='ignore') for token in tokens]

    # Since we want this to find full URLs and not just potential domain names, we want
    # to ensure that the tokens have at least "http" or "/" in them.
    tokens = list(set([t for t in tokens if ('http' in t or 'ftp' in t or ('/' in t and '.' in t)) and len(t) >= 8]))

    # Remove any tokens that look like they're probably bad based on the regex statements above.
    tokens = [t for t in tokens if not all(x in t for x in ['(', ')'])]
    tokens = [t for t in tokens if not all(x in t for x in ['<', '>'])]
    tokens = [t for t in tokens if not all(x in t for x in ['[', ']'])]
    tokens = [t for t in tokens if not all(x in t for x in ['{', '}'])]
    tokens = [t for t in tokens if not any(x in t for x in ['\t', '\n', '\r'])]
    tokens = [t for t in tokens if t[:1].isalpha() or t[:1].isdigit()]
    tokens = [t for t in tokens if not t.count('\'') > 1]
    tokens = [t for t in tokens if not t.count('\"') > 1]

    # Return a list of the tokens in ASCII format.
    return tokens


def _ascii_find_urls(bytes, mimetype, extra_tokens=True):
    """ This function finds URLs inside of ASCII bytes. """

    tokens = _tokenize(bytes, mimetype, extra_tokens=extra_tokens)

    return tokens


def _html_find_urls(bytes, mimetype, base_url=None):
    """ This function finds URLs inside of valid HTML bytes. """

    def _recursive_tag_values(tag, values=[]):
        """ This sub-function recursively loops through all of the tags to get all of the attribute values. """

        if hasattr(tag, 'children'):
            for child in tag.children:
                if hasattr(child, 'attrs'):
                    for key in child.attrs:
                        if isinstance(child.attrs[key], list):
                            for value in child.attrs[key]:
                                values.append(value)
                        elif isinstance(child.attrs[key], str):
                            values.append(child.attrs[key])

                    values = _recursive_tag_values(child, values)

        return values

    # Only convert the ASCII bytes to HTML.
    ascii_bytes = b''.join(re.compile(b'[\x00\x09\x0A\x0D\x20-\x7E]{8,}').findall(bytes))
    ascii_bytes = ascii_bytes.replace(b'\x00', b'')

    # Store all of the URLs we find.
    urls = []

    # Convert the bytes into soup. Also try url decoding the bytes to bypass some obfuscation.
    soups = []
    soups.append(BeautifulSoup(ascii_bytes, 'lxml'))
    soups.append(BeautifulSoup(ascii_bytes, 'html.parser'))
    try:
        soups.append(BeautifulSoup(urllib.parse.unquote(str(ascii_bytes)), 'lxml'))
    except:
        pass

    # Loop over both soups.
    for soup in soups:

        # Find any URLs embedded in script + document.write JavaScript.
        # \r\n\r\ndocument.write(unescape('<meta HTTP-EQUIV="REFRESH" content="0; url=http://somebadsite.com/catalog/index.php">'));\r\n\r\n
        script_urls = []
        script_tags = soup.find_all('script')
        for script_tag in script_tags:
            for tag_content in script_tag.contents:
                if 'document.write' in tag_content.lower():
                    # Find the last position of the ( character, which should denote where the
                    # code that they are writing to the page begins. Also find the position of
                    # the first ) character which should denote where the code ends.
                    code_begin = tag_content.rfind('(')
                    code_end = tag_content.find(')')
                    code = tag_content[code_begin+1:code_end]
                    # Strip off any ' or " quotes.
                    if code.startswith('\'') and code.endswith('\''):
                        code = code[1:-1]
                    if code.startswith('"') and code.endswith('"'):
                        code = code[1:-1]
                    # Turn the string into bytes and feed it back into the _html_find_urls function.
                    code = code.encode()
                    script_urls += _html_find_urls(code, mimetype)

        # Find any URLs embedded in <script> tags. Use the _ascii_find_urls function to try and catch everything.
        for script_tag in script_tags:
            script_urls += _ascii_find_urls(str(script_tag).encode('utf-8'), mimetype)

        # Find any meta-refresh URLs.
        # <meta HTTP-Equiv="refresh" content="0; URL=UntitledNotebook1.html">
        meta_urls = []
        meta_tags = soup.find_all('meta')
        for meta_tag in meta_tags:
            for key in meta_tag.attrs:
                if key.lower() == 'content':
                    value = meta_tag.attrs[key]
                    if 'url=' in value.lower():
                        split_value = value.split('=', 1)
                        url = split_value[1]
                        # Remove any quotes around the URL.
                        if url.startswith('"') and url.endswith('"'):
                            url = url[1:-1]
                        if url.startswith("'") and url.endswith("'"):
                            url = url[1:-1]
                        meta_urls.append(url)

        # Hacky way to find URLs in the CSS.
        css_urls = re.compile(r'url\((.*?)\)').findall(str(soup))
        
        # Make sure none of the CSS URLs are in quotes.
        for u in css_urls[:]:
            if u.startswith('\'') and u.endswith('\''):
                css_urls.remove(u)
                css_urls.append(u[1:-1])
            if u.startswith('\"') and u.endswith('\"'):
                css_urls.remove(u)
                css_urls.append(u[1:-1])

        # Look to see if there is a "base" HTML tag specified. This is the "baseStriker" method.
        for tag in soup.find_all('base'):
            try:
                if tag['href']:
                    base_url = tag['href'].replace('\\\\', '//')
            except:
                pass

        # If we were given a base URL, only extract specific tag values that are likely
        # to be URLs. Otherwise, we would end up with joined URLs for every single tag
        # attribute value that exists in the HTML, which is not the correct behavior.
        if base_url:

            # Join any of the CSS URLs we found.
            for css_url in css_urls:
                urls.append(urljoin(base_url, css_url))

            # Join any of the script URLs we found.
            for script_url in script_urls:
                urls.append(urljoin(base_url, script_url))

            # Join any of the meta-refresh URLs we found.
            for meta_url in meta_urls:
                urls.append(urljoin(base_url, meta_url))

            # Get all of the action URLs.
            for tag in soup.find_all(action=True):
                urls.append(urljoin(base_url, tag['action']))

            # Get all of the background URLs.
            for tag in soup.find_all(background=True):
                urls.append(urljoin(base_url, tag['background']))

            # Get all of the href URLs.
            for tag in soup.find_all(href=True):
                urls.append(urljoin(base_url, tag['href']))

            # Get all of the src URLs.
            for tag in soup.find_all(src=True):
                urls.append(urljoin(base_url, tag['src']))

            # Get all of the xmlns URLs.
            for tag in soup.find_all(xmlns=True):
                urls.append(urljoin(base_url, tag['xmlns']))

        # We weren't given a base URL, so just search for URLs by getting every single
        # tag attribute value. That way we will catch everything regardless of the attribute name.
        else:
            urls = _recursive_tag_values(soup)
            urls += css_urls
            urls += meta_urls
            urls += script_urls

        # As a last-ditch effort, find URLs in the visible text of the HTML. However,
        # we only want to add strings that are valid URLs as they are. What we do not
        # want is to add every string as a potential URL, since if a base_url was given,
        # we will likely end up with a joined URL for every string found in the HTML.
        for s in soup.stripped_strings:
            if is_valid(s):
                urls.append(s)

        # Remove any newlines from the potential URLs. Some HTML has newlines
        # after the href=" part before the actual URL begins. This renders
        # correctly in web browsers but is otherwise considered an invalid
        # URL by the is_valid function.
        urls = [u.strip() for u in urls]

        # Remove any leading //'s from the URLs.
        urls = [u[2:] if u.startswith('//') else u for u in urls]

    return urls


def _pdf_find_urls(bytes, mimetype):
    """ This function finds URLs inside of PDF bytes. """

    # Start with only the ASCII bytes. Limit it to 12+ character strings.
    try:
        ascii_bytes = b' '.join(re.compile(b'[\x00\x09\x0A\x0D\x20-\x7E]{12,}').findall(bytes))
        ascii_bytes = ascii_bytes.replace(b'\x00', b'')
    except:
        return []

    urls = []

    # Find the embedded text sandwiched between [ ]
    embedded_text = set(re.compile(b'(\[(\([\x20-\x27\x2A-\x7E]{1,3}\)[\-\d]*){5,}\])').findall(ascii_bytes))

    # Get the text inside the parentheses. This catches URLs embedded in the text of the PDF that don't
    # use the normal "URI/URI()>>" method.
    for match in embedded_text:
        text = match[0]
        parentheses_text = b''.join(re.compile(b'\((.*?)\)').findall(text))
        urls.append(parentheses_text)

    # Find any URLs that use the "URI/URI()>>" method.
    urls += re.compile(b'\/URI\s*\((.*?)\)\s*>>').findall(ascii_bytes)

    if urls:
        # PDF URLs escape certain characters. We want to remove any of the escapes (backslashes)
        # from the URLs so that we get the original URL.
        urls = [u.replace(b'\\', b'') for u in urls]

    return urls


def find_urls(thing, base_url=None, mimetype=None, log=False):
    """ This function uses several methods to extract URLs from 'thing', which can be a string or raw bytes.
        If you supply the base URL, it will attempt to use it with urljoin to create full URLs from relative paths. """

    if log:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(name)s.%(funcName)s +%(lineno)s: %(levelname)-8s %(message)s')
        logger = logging.getLogger(__name__)

    # Convert "thing" to bytes if it is a string.
    try:
        if isinstance(thing, str):
            thing = thing.encode(encoding='ascii', errors='ignore')
    except:
        if log:
            logger.exception('Unable to convert thing to bytes.')
        return []

    # Store any URLs we find in the bytes.
    all_urls = []

    # Continue if we have bytes.
    if isinstance(thing, bytes):

        # Return an empty list if we failed to get the mimetype.
        try:
            if not mimetype:
                mimetype = magic.from_buffer(thing)
        except:
            if log:
                logger.exception('Unable to get mimetype from the bytes buffer.')
            return []

        mimetype = mimetype.lower()

        # If the bytes are HTML...
        if 'html' in mimetype:
            try:
                all_urls += _html_find_urls(thing, mimetype, base_url)
            except:
                if log:
                    logger.exception('Error when finding HTML URLs.')

        # If the bytes are a PDF...
        elif 'pdf' in mimetype:
            try:
                all_urls += _pdf_find_urls(thing, mimetype)
            except:
                if log:
                    logger.exception('Error when finding PDF URLs.')

        # If the bytes are an RFC 822 e-mail...
        elif 'rfc 822' in mimetype:
            return []

        # If the bytes are ASCII or Unicode text...
        elif 'ascii' in mimetype or 'text' in mimetype:
            try:
                all_urls += _html_find_urls(thing, mimetype, base_url)
            except:
                if log:
                    logger.exception('Error when finding ASCII/HTML URLs.')

            try:
                all_urls += _ascii_find_urls(thing, mimetype)
            except:
                if log:
                    logger.exception('Error when finding ASCII URLs.')

            try:
                all_urls += _pdf_find_urls(thing, mimetype)
            except:
                if log:
                    logger.exception('Error when finding ASCII/PDF URLs.')

        # If the bytes are anything else...
        else:

            # Try to treat the bytes as a PDF and find URLs.
            try:
                all_urls += _pdf_find_urls(thing, mimetype)
            except:
                if log:
                    logger.exception('Error when finding unknown/PDF URLs.')

            # If we don't know how to handle this mimetype, the bytes are likely just "data".
            # In that case, we don't want to find all possible ASCII URLs, as it will result
            # in a lot of bad URLs. Try to treat the bytes as ASCII and find URLs.
            try:
                all_urls += _ascii_find_urls(thing, mimetype, extra_tokens=False)
            except:
                if log:
                    logger.exception('Error when finding unknown/ASCII URLs.')

    # Make sure we only have valid URLs.
    valid_urls = []
    for url in list(set(all_urls)):
        try:
            # If the URL is valid as-is, just add it to the list.
            if is_valid(url):
                valid_urls.append(url)

            # The URL is not valid. If we were given a base URL, try joining them and checking if the result is valid.
            elif base_url:
                joined_url = urljoin(base_url, url)
                if is_valid(joined_url):
                    valid_urls.append(joined_url)
        except:
            pass

    # For the edge cases of HTML files where we didn't find any URLs, treat it as an ASCII file
    # and re-find any URLs that way.
    if not valid_urls and 'html' in mimetype:
        try:
            for url in _ascii_find_urls(thing, mimetype):
                # If the URL is valid as-is, just add it to the list.
                if is_valid(url):
                    valid_urls.append(url)

                # The URL is not valid. If we were given a base URL, try joining them and checking if the result is valid.
                elif base_url:
                    joined_url = urljoin(base_url, url)
                    if is_valid(joined_url):
                        valid_urls.append(joined_url)
        except:
            pass

    # Return the valid URLs in ASCII form.
    ascii_urls = []
    for url in valid_urls:
        try:
            if isinstance(url, str):
                ascii_urls.append(url)

            if isinstance(url, bytes):
                ascii_urls.append(url.decode('ascii', errors='ignore'))
        except:
            pass

    # Check if any of the URLs are Proofpoint URLs and try to decode them.
    for url in ascii_urls[:]:
        if 'urldefense.proofpoint.com/v2/url' in url:
            try:
                query_u=parse_qs(urlparse(url).query)['u'][0]
                decoded_url = query_u.replace('-3A', ':').replace('_', '/').replace('-2D', '-')
                if is_valid(decoded_url):
                    ascii_urls.append(decoded_url)
            except:
                if log:
                    logger.exception('Error decoding Proofpoint URL: {}'.format(url))

    # Check if any of the URLs are Outlook safelinks and try to decode them.
    for url in ascii_urls[:]:
        if 'safelinks.protection.outlook.com' in url:
            try:
                query_url=parse_qs(urlparse(url).query)['url'][0]
                decoded_url = urllib.parse.unquote(query_url)
                if is_valid(decoded_url):
                    ascii_urls.append(decoded_url)
            except:
                if log:
                    logger.exception('Error decoding Outlook safelinks URL: {}'.format(url))

    # Check if any of the URLs are Google redirection URLs and try to decode them.
    for url in ascii_urls[:]:
        if 'www.google.com/url?' in url:
            try:
                query_url=parse_qs(urlparse(url).query)['q'][0]
                decoded_url = urllib.parse.unquote(query_url)
                if is_valid(decoded_url):
                    ascii_urls.append(decoded_url)
            except:
                if log:
                    logger.exception('Error decoding Google redirection URL: {}'.format(url))

    # Check if any of the URLs are Barracuda Link Protect URLs and try to decode them.
    for url in ascii_urls[:]:
        if 'linkprotect.cudasvc.com' in url:
            try:
                query_url=parse_qs(urlparse(url).query)['a'][0]
                decoded_url = urllib.parse.unquote(query_url)
                if is_valid(decoded_url):
                    ascii_urls.append(decoded_url)
            except:
                if log:
                    logger.exception('Error decoding Barracuda Link Protect URL: {}'.format(url))

    # Add an unquoted version of each URL to the list.
    for url in ascii_urls[:]:
        ascii_urls.append(urllib.parse.unquote(url))

    # Add http:// to the beginning of each URL if it isn't there already. This lets us properly
    # catch URLs that may not have the scheme on the front of them.
    ascii_urls = ['http://' + u if not u.lower().startswith('http') and not u.lower().startswith('ftp') else u for u in ascii_urls]

    # Remove any trailing "/" from the URLs so that they are consistent with how they go in CRITS.
    ascii_urls = [u[:-1] if u.endswith('/') else u for u in ascii_urls]

    return sorted(list(set(ascii_urls)))


def is_valid(url, fix=True):
    """ Returns True if this is what we consider to be a valid URL.

        A valid URL has:
            * http OR https scheme
            * a valid TLD

        If there is no scheme, it will check the URL assuming the scheme is http.

        Returns False if the URL is not valid.
    """

    try:
        # Convert the url to a string if we were given it as bytes.
        if isinstance(url, bytes):
            url = url.decode('ascii', errors='replace')

        # Hacky way to deal with URLs that have a username:password notation.
        user_pass_url = ''

        # Check for no scheme and assume http.
        split_url = urlsplit(url)

        # If there is no scheme, there is a higher chance that this might not actually be a URL.
        # For example, it might be something that resembles a URL that got pulled out of random bytes.
        # As such, we can probably safely exclude URLs that have unusual characters in them.
        if not split_url.scheme:
            invalid_chars = ['\'']
            if any(c in url for c in invalid_chars):
                return False

        # Append the http scheme to the URL if it doesn't have any scheme.
        if fix and not split_url.scheme:
            split_url = urlsplit('http://{}'.format(url))

        # Check for the edge case of results returned by find_urls, such as google.com URLs
        # like: http://google.com#default#userData
        if split_url.netloc and not split_url.path and split_url.fragment:
            return False

        # Check if the netloc has a ':' in it, which indicates that
        # there is a port number specified. We need to remove that in order
        # to properly check if it is a valid IP address.
        if ':' in split_url.netloc:
            netloc = split_url.netloc.split(':')[0]
        else:
            netloc = split_url.netloc

        # Make sure the URL doesn't have a \ character in it.
        if '\\' in url:
            return False

        # Some quick and dirty tests to detect invalid characters from different parts of the URL.
        # Domain names need to have only: a-z, 0-9, -, and . But due to how urlsplit works, they
        # might also contain : and @ if there is a user/pass or port number specified.
        if re.compile(r'([^a-zA-Z0-9\-\.\:\@]+)').findall(split_url.netloc):
            return False

        # Check if the valid URL conditions are now met.
        if split_url.scheme == 'http' or split_url.scheme == 'https' or split_url.scheme == 'ftp':

            # Look for the edge case of the URL having a username:password notation.
            if ':' in split_url.netloc and '@' in split_url.netloc:
                user_pass = re.compile(r'(.*?:.*?@)').findall(split_url.netloc)[0]
                user_pass_url = url.replace(user_pass, '')
                split_url = urlsplit(user_pass_url)
                netloc = split_url.netloc

            # Check the netloc. Check if it is an IP address.
            try:
                ipaddress.ip_address(netloc)
                return True
            # If we got an exception, it must be a domain name.
            except:

                # Hacky way to out which version of the URL we need to check.
                if user_pass_url:
                    url_to_check = user_pass_url
                else:
                    url_to_check = url

                # Hacky way to deal with FTP URLs since the tld package cannot handle them.
                if split_url.scheme == 'ftp':
                    url_to_check = url_to_check.replace('ftp', 'http')

                # Check the URL for a valid TLD.
                res = get_tld(url_to_check, fix_protocol=True, as_object=True)

                # The tld package likes to consider single words (like "is") as a valid domain. To fix this,
                # we want to only consider it a valid URL if there is actually a suffix. Additionally, to weed
                # out "URLs" that are probably e-mail addresses or other garbage, we do not want to consider
                # anything that has invalid characters in it.
                if res.fld and res.tld and res.domain:
                    if all(ord(c) == 45 or ord(c) == 46 or (48 <= ord(c) <= 57) or (65 <= ord(c) <= 90) or (97 <= ord(c) <= 122) for c in netloc):

                        # Finally, check if all of the characters in the URL are ASCII.
                        if all(32 <= ord(c) <= 126 for c in url):
                            return True

        # Return False by default.
        return False
    except:
        return False
