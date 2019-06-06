
from modeltranslation.translator import translator

from articles.models import Article, ArticleTag, ArticleType


translator.register(Article, fields=['title', 'description', 'text'])
translator.register(ArticleTag, fields=['text'])
translator.register(ArticleType, fields=['name'])
