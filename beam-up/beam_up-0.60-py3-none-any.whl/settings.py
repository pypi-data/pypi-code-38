from .processors import JinjaProcessor, MarkdownProcessor, PlainProcessor
from .builders import BlogBuilder, PagesBuilder, StaticFilesBuilder, SitemapBuilder
from .loaders import FileLoader

SETTINGS = {
    'defaults' : {
        'src-dir' : 'src',
        'build-dir' : 'build',
    },
    'loaders' : [
        {
            'scheme' : 'file',
            'loader' : FileLoader
        }
    ],
    'builders' : [
        {
            'builder' : BlogBuilder,
            'name' : 'blog'
        },
        {
            'builder' : PagesBuilder,
            'name' : 'pages'
        },
        {
            'builder' : StaticFilesBuilder,
            'providers' : ['static_file'], 
            'name' : 'static_files'
        },
        {
            'builder' : SitemapBuilder,
            'name' : 'sitemap'
        },
    ],
    'processors' : [
        {
            'type' : 'html',
            'processors' : [JinjaProcessor],
            'name' : 'HTML'
        },
        {
            'type' : 'md',
            'processors' : [MarkdownProcessor, JinjaProcessor],
            'name' : 'Markdown'
        },
        {
            'type' : 'plain',
            'processors' : [PlainProcessor],
            'name' : 'Plain'
        }
    ],
}