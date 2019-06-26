from linkable import patterns


def validate_hashtag(value):
    return patterns.hashtag_pattern.fullmatch(value) is not None


def validate_github_mention(value):
    return patterns.github_mention_pattern.fullmatch(value) is not None


def validate_twitter_mention(value):
    return patterns.twitter_mention_pattern.fullmatch(value) is not None


def validate_email(value):
    return patterns.email_pattern.fullmatch(value) is not None


def validate_url(value):
    return patterns.url_pattern.fullmatch(value) is not None
