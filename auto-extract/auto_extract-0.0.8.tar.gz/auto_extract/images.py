# <figure> should maybe use some weighting
# background-url should also be allowed

# Also return most likely logo (logo, favicon??, first image?, icon)
import re
from auto_extract.utils import urljoin

# "https://techcrunch.com/2017/05/05/amazon-fire-tv-code-hints-at-plans-for-single-sign-on-support/"


def general_ok_img(img_candidate, original_url, wrong_imgs):
    link = None
    if img_candidate.tag == 'img':
        if 'src' not in img_candidate.attrib:
            return False
        link = img_candidate.attrib['src']
    else:
        if 'content' in img_candidate.attrib:
            link = img_candidate.attrib['content']
        elif 'style' in img_candidate.attrib:
            tmp = re.findall(
                r'background-image:[ ]*url\((http[^)]+)', img_candidate.attrib['style'])
            if tmp:
                link = tmp[0]
    if link is None:
        return False
    # if link longer than 1000 chars, drop it
    if len(link) > 1000:
        return False
    # # if link does not start with "http", drop it
    if not urljoin(original_url, link).startswith('http'):
        return False
    # if link attributes contain one of the wrong atts, drop it
    if any([any([w in img_candidate.attrib[a] for w in wrong_imgs])
            for a in img_candidate.attrib]):
        return False
    return True


def dimensions_ok(img_candidate):
    try:
        if 'height' in img_candidate.attrib and int(img_candidate.attrib['height']) < 100:
            return False
        if 'width' in img_candidate.attrib and int(img_candidate.attrib['width']) < 100:
            return False
    except ValueError:
        pass
    return True


def get_images(tree, original_url, title_index, wrong_atts=None):
    # meta = tree.xpath("//meta[@property='og:image']/@content")
    # meta += tree.xpath("//link[contains(@rel, 'icon')]/@href")
    # meta += tree.xpath("//meta[@property='name:image']/@content")
    # meta += tree.xpath("//link[@rel='img_src']/@content")
    # if title_index is None:
    #     if not meta:
    #         return None
    #     else:
    #         return meta
    if title_index is None:
        return None
    if wrong_atts is None:
        wrong_atts = ['adsense', 'icon', 'logo', 'advert', 'toolbar', 'footer', 'layout', 'banner']
        # dit recoden in een tree.iter() loop, en dan ook de "node index"/num noteren hier.
    img_candidates = tree.xpath('//img[string-length(@src) > 3]')
    img_candidates += tree.xpath('//meta[contains(@property, "image")]')
    img_candidates += tree.xpath('//*[contains(@style, "background-image")]')
    ok_images = []
    for img_candidate in img_candidates:
        if general_ok_img(img_candidate, original_url, wrong_atts):
            if img_candidate.tag == 'img':
                if dimensions_ok(img_candidate):
                    ok_images.append(img_candidate)
            else:
                ok_images.append(img_candidate)
    images_and_indices = []

    for num, node in enumerate(tree.iter()):
        if node in ok_images:
            images_and_indices.append((node, num))
    ranked_images = sorted(images_and_indices, key=lambda x: abs(x[1] - title_index))

    images = []
    for x in ranked_images:
        val = None
        if 'src' in x[0].attrib:
            val = x[0].attrib['src']
        elif 'content' in x[0].attrib:
            val = x[0].attrib['content']
        elif 'style' in x[0].attrib:
            tmp = re.findall(r'background-image:[ ]*url\((http[^)]+)', x[0].attrib['style'])
            if tmp:
                val = tmp[0]
        if val is not None:
            val = urljoin(original_url, val)
            if val not in images:
                images.append(val)
    return images
