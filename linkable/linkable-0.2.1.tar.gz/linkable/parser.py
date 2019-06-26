from linkable import patterns, validators
from linkable.helpers import LazyAttribute


class Linkable:
    _validators_list = (
        'hashtag',
        'mention',
        'email',
        'url'
    )

    def __init__(self, text, mention_style: str='twitter'):
        self.mention_style = mention_style
        self.text = text
        self.validators = dict(
            email=validators.validate_email,
            url=validators.validate_url,
            hashtag=validators.validate_hashtag,
            mention=(
                validators.validate_twitter_mention
                if self.mention_style == 'twitter' else
                validators.validate_github_mention
            )
        )

    def __str__(self):
        return self.replaced_text

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.__str__() == other

    @LazyAttribute
    def replaced_text(self):
        return self.replace_links(self.text)

    def replace_links(self, text):
        return patterns.word_pattern.sub(self.first_replacer, text)

    def first_replacer(self, match):
        value = match.group()
        if patterns.brackets_pattern.search(value) is not None:
            return patterns.brackets_pattern.sub(
                self.second_replacer,
                value
            )
        return self.second_replacer(match)

    def second_replacer(self, match):
        value = match.group()
        if patterns.dirty_hashtag_pattern.search(value) is not None:
            return patterns.dirty_hashtag_pattern.sub(
                self.main_replacer,
                value
            )
        return self.main_replacer(match)

    def main_replacer(self, match):
        value = match.group()
        for validator_name in self._validators_list:
            if self.validators[validator_name](value) is not False:
                return getattr(
                    self, 'replace_%s' % validator_name
                )(value)
        return value

    def replace_hashtag(self, value):
        return '<a href="/hashtag/{value}">{value}</a>'.format(value=value)

    def replace_mention(self, value):
        return '<a href="/{value}">{value}</a>'.format(value=value)

    def replace_url(self, value):
        url = value
        if patterns.url_scheme_pattern.match(url) is None:
            url = 'http://' + url
        return '<a href="{url}">{value}</a>'.format(url=url, value=value)

    def replace_email(self, value):
        return '<a href="mailto:{value}">{value}</a>'.format(value=value)


class LinkableList(Linkable):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hashtags = []
        self.mentions = []
        self.urls = []
        self.emails = []
        self.replace_links(self.text)

    def replace_mention(self, value):
        self.mentions.append(value)
        return super().replace_mention(value)

    def replace_hashtag(self, value):
        self.hashtags.append(value)
        return super().replace_hashtag(value)

    def replace_email(self, value):
        self.emails.append(value)
        return super().replace_email(value)

    def replace_url(self, value):
        self.urls.append(value)
        return super().replace_url(value)

    @property
    def links(self):
        return self.hashtags + self.mentions + self.urls + self.emails
