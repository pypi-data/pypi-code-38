# Original source:
#   https://github.com/RealGeeks/wp_export_parser/blob/master/wp_export_parser/parse_shortcodes.py

import re


def do_caption(tag_atts, tag_contents):
    """
    From wordpress source: https://github.com/WordPress/WordPress/blob/master/wp-includes/media.php#L620
    return '<div ' . $id . 'class="wp-caption ' . esc_attr($align) . '" style="width: ' . (10 + (int) $width) . 'px">'
    . do_shortcode( $content ) . '<p class="wp-caption-text">' . $caption . '</p></div>';
    
    """
    if not tag_atts:
        return ''
    tag_atts = dict([(a[0], a[1]) for a in tag_atts])

    if not tag_atts.get('caption'):
        # new-style caption shortcode (caption in body with image)
        match_object = re.search(
            r'((?:<a [^>]+>\s*)?<img [^>]+>(?:\s*</a>)?)(.*)',
            tag_contents,
            flags=re.IGNORECASE)
        if match_object:
            tag_contents = match_object.group(1)
            tag_atts['caption'] = match_object.group(2).strip()
    else:
        # old-style caption shortcode (caption="caption")
        #$attr['caption'] = wp_kses( $attr['caption'], 'post' );
        pass

    classes = ['wp-caption']
    if 'align' in tag_atts:
        classes.append(tag_atts.get('align'))
    return "<figure id=\"{id}\" class=\"{classes}\">{content}<figcaption class=\"wp-caption-text\">{caption}</figcaption></figure>".format(
        id=tag_atts.get('id', ''),
        classes=' '.join(classes),
        width=int(tag_atts.get('width', 0)) + 10,
        content=tag_contents,
        caption=tag_atts.get('caption', ''),
    )


TAGS_WE_CAN_PARSE = {
    'caption': do_caption,
}


def replace_tags(match):
    tag_name = match.group(2)
    tag_atts = match.group(3)
    tag_contents = match.group(5)
    if tag_name in TAGS_WE_CAN_PARSE:
        tag_atts = parse_shortcode_atts(tag_atts)
        return TAGS_WE_CAN_PARSE[tag_name](tag_atts, tag_contents)


def parse_shortcode_atts(atts):
    pattern = r'(\w+)\s*=\s*"([^"]*)"(?:\s|$)|(\w+)\s*=\s*\'([^\']*)\'(?:\s|$)|(\w+)\s*=\s*([^\s\'"]+)(?:\s|$)|"([^"]*)"(?:\s|$)|(\S+)(?:\s|$)'
    return re.findall(pattern, atts)


def parse_shortcodes(post_body):
    """
    I stole this shortcode regex from Wordpress's source.  It is very confusing.
    """
    tagregexp = '|'.join([re.escape(t) for t in TAGS_WE_CAN_PARSE.keys()])
    pattern = re.compile(
        '\\[(\\[?)(' + tagregexp +
        ')\\b([^\\]\\/]*(?:\\/(?!\\])[^\\]\\/]*)*?)(?:(\\/)\\]|\\](?:([^\\[]*(?:\\[(?!\\/\\2\\])[^\\[]*)*)\\[\\/\\2\\])?)(\\]?)'
    )
    return re.sub(pattern, replace_tags, post_body)
