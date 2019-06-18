
from lxml import html as lxml_html


def get_header_text(el):
    return el.xpath('string(./*[self::h1 or self::h2 or self::h3 or self::h4]/text())')


def get_lines(el):
    return [dict(begin=ln.get('begin'), line=ln.text) for ln in el.xpath('./*[@begin]')]


def get_act_lines(act_content):
    return [
        dict(speaker_lines, speaker=speaker_block.get('class'))
        for speaker_block in act_content
        for speaker_lines in get_lines(speaker_block)
    ]


class TranscriptHtml(object):
    EPISODE_TITLE_PATH = '//div[@id="content"]//header'
    ACT_PATH = '//div[@class="act"]'
    ACT_SCRIPT_PATH = './div[@class="act-inner"]/div'

    def __init__(self, html_string=None):
        self.html_string = html_string
        self.document_tree = lxml_html.fromstring(self.html_string)

    def extract_episode_title(self):
        episode_info = self.document_tree.xpath(TranscriptHtml.EPISODE_TITLE_PATH)
        return get_header_text(episode_info[0]) if episode_info else None

    def extract_transcript(self):
        acts = self.document_tree.xpath(TranscriptHtml.ACT_PATH)

        act_info_generator = (
            (dict(act_number=i, act_id=act.get('id'), act_title=get_header_text(act)), act)
            for i, act in enumerate(acts, start=1)
        )

        return [
            {**transcript_line, **act_info}
            for act_info, act in act_info_generator
            for transcript_line in get_act_lines(act.xpath(TranscriptHtml.ACT_SCRIPT_PATH))
        ]

    def to_json(self):
        return dict(
            episode_title=self.extract_episode_title(),
            transcript=self.extract_transcript()
        )
