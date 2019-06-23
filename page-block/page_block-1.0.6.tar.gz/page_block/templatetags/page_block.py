# coding=utf-8
"""Template tags."""

import django.utils.translation
from django import template
from django.conf import settings
from django.template.context import Context
from django.template.engine import Engine

import django_tag_parser

from page_block.models import PageBlock, PageBlockTranslation

register = template.Library()


ERROR_MESSAGE = (
    "Missing block for slug {} for language {}. Languages found {}."
)


@register.tag("page_block")
def do_page_block(parser, token):
    """Renders page block."""
    parser_parse = django_tag_parser.TagParser(
        args=["block_type"],
        opt_kwargs=["template", "language"]
    )

    return PageNode(parser_parse.parse(parser, token))


class PageNode(template.Node):
    """Page node."""

    def __init__(self, parsed_args: django_tag_parser.ParsedArguments) -> None:
        super().__init__()
        self.parsed_args = parsed_args

    def __prepare_context(self, template_context) -> Context:
        resolved = self.parsed_args.resolve(template_context)
        language = resolved.get('language', None)
        block_type = resolved['block_type']
        template_name = resolved.get('template', 'page_block/card.html')

        if language is None:                                    # Right now this case is not used, but soon will be
            language = django.utils.translation.get_language()  # pragma: no cover

        block = PageBlock.objects.get_language_version(block_type, language)

        if block is None and getattr(settings, 'SHOW_MISSING_PAGE_BLOCKS', False):
            try:
                languages = [tb.language for tb in PageBlock.objects.get(block_type=block_type).translations.all()]
            except PageBlock.DoesNotExist:
                languages = "None"

            error_message = ERROR_MESSAGE.format(block_type, language, languages)
            block = PageBlockTranslation(
                title="Missing block",
                contents_html=error_message
            )

        return Context({
            "page_block": block,
            "template_name": template_name
        })

    def render(self, context):
        ctx = self.__prepare_context(context)
        engine = Engine.get_default()
        to_be_rendered = engine.get_template(ctx['template_name'])
        return to_be_rendered.render(ctx)
