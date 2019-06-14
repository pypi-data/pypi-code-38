import setuptools

with open("README.md", 'r') as f:
    long_description = f.read()

with open("VERSION", 'r') as f:
    version = f.read()

setuptools.setup(
    name="twitter-fire-scraper",
    version=version,

    author="Henry Post",
    author_email="HenryFBP@gmail.com",

    description="A tool to scrape data about fires from Twitter.",
    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://github.com/twitter-fire-scraper-analytics/twitter-fire-scraper",

    package_data = {
        'twitter-fire-scraper': [
            'data/*.yml',
            'templates/*.html'
        ]
    },

    packages=setuptools.find_packages(),
    install_requires=[
        "click",
        "itsdangerous",
        "nltk",
        "oauthlib",
        "requests",
        "requests-oauthlib",
        "six",
        "textblob",
        "tweepy",
        "Flask",
        "Jinja2",
        "MarkupSafe",
        "Werkzeug",
        "tmdbsimple",
        "colorama",
        "pymongo",
        "typing",
        "pyyaml",
        "flask_pymongo",
        "dnspython",
        "chardet",
        "certifi",
        "numpy",
        "matplotlib",
    ],

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
)
