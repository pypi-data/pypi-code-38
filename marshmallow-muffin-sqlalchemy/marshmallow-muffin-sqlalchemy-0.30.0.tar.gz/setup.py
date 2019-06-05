# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['marshmallow_sqlalchemy']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.3.4,<2.0.0', 'marshmallow-muffin>=3.0.1,<4.0.0']

setup_kwargs = {
    'name': 'marshmallow-muffin-sqlalchemy',
    'version': '0.30.0',
    'description': 'Marshmallow Muffin SQL Alchemy',
    'long_description': '**********************\nmarshmallow-sqlalchemy\n**********************\n\n|pypi-package| |build-status| |docs| |marshmallow23| |black|\n\nHomepage: https://marshmallow-sqlalchemy.readthedocs.io/\n\n`SQLAlchemy <http://www.sqlalchemy.org/>`_ integration with the  `marshmallow <https://marshmallow.readthedocs.io/en/latest/>`_ (de)serialization library.\n\nDeclare your models\n===================\n\n.. code-block:: python\n\n    import sqlalchemy as sa\n    from sqlalchemy.ext.declarative import declarative_base\n    from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref\n\n    engine = sa.create_engine("sqlite:///:memory:")\n    session = scoped_session(sessionmaker(bind=engine))\n    Base = declarative_base()\n\n\n    class Author(Base):\n        __tablename__ = "authors"\n        id = sa.Column(sa.Integer, primary_key=True)\n        name = sa.Column(sa.String)\n\n        def __repr__(self):\n            return "<Author(name={self.name!r})>".format(self=self)\n\n\n    class Book(Base):\n        __tablename__ = "books"\n        id = sa.Column(sa.Integer, primary_key=True)\n        title = sa.Column(sa.String)\n        author_id = sa.Column(sa.Integer, sa.ForeignKey("authors.id"))\n        author = relationship("Author", backref=backref("books"))\n\n\n    Base.metadata.create_all(engine)\n\nGenerate marshmallow schemas\n============================\n\n.. code-block:: python\n\n    from marshmallow_sqlalchemy import ModelSchema\n\n\n    class AuthorSchema(ModelSchema):\n        class Meta:\n            model = Author\n\n\n    class BookSchema(ModelSchema):\n        class Meta:\n            model = Book\n            # optionally attach a Session\n            # to use for deserialization\n            sqla_session = session\n\n\n    author_schema = AuthorSchema()\n\n(De)serialize your data\n=======================\n\n.. code-block:: python\n\n    author = Author(name="Chuck Paluhniuk")\n    author_schema = AuthorSchema()\n    book = Book(title="Fight Club", author=author)\n    session.add(author)\n    session.add(book)\n    session.commit()\n\n    dump_data = author_schema.dump(author).data\n    # {\'books\': [123], \'id\': 321, \'name\': \'Chuck Paluhniuk\'}\n\n    author_schema.load(dump_data, session=session).data\n    # <Author(name=\'Chuck Paluhniuk\')>\n\nGet it now\n==========\n::\n\n   pip install -U marshmallow-sqlalchemy\n\n\nDocumentation\n=============\n\nDocumentation is available at https://marshmallow-sqlalchemy.readthedocs.io/ .\n\nProject Links\n=============\n\n- Docs: https://marshmallow-sqlalchemy.readthedocs.io/\n- Changelog: https://marshmallow-sqlalchemy.readthedocs.io/en/latest/changelog.html\n- PyPI: https://pypi.python.org/pypi/marshmallow-sqlalchemy\n- Issues: https://github.com/marshmallow-code/marshmallow-sqlalchemy/issues\n\nLicense\n=======\n\nMIT licensed. See the bundled `LICENSE <https://github.com/marshmallow-code/marshmallow-sqlalchemy/blob/dev/LICENSE>`_ file for more details.\n\n\n.. |pypi-package| image:: https://badgen.net/pypi/v/marshmallow-sqlalchemy\n    :target: https://pypi.org/project/marshmallow-sqlalchemy/\n    :alt: Latest version\n.. |build-status| image:: https://badgen.net/travis/marshmallow-code/marshmallow-sqlalchemy/dev\n    :target: https://travis-ci.org/marshmallow-code/marshmallow-sqlalchemy\n    :alt: Travis-CI\n.. |docs| image:: https://readthedocs.org/projects/marshmallow-sqlalchemy/badge/\n   :target: http://marshmallow-sqlalchemy.readthedocs.io/\n   :alt: Documentation\n.. |marshmallow23| image:: https://badgen.net/badge/marshmallow/2,3?list=1\n    :target: https://marshmallow.readthedocs.io/en/latest/upgrading.html\n    :alt: marshmallow 3 compatible\n.. |black| image:: https://badgen.net/badge/code%20style/black/000\n    :target: https://github.com/ambv/black\n    :alt: code style: black\n',
    'author': 'Alex Sansone',
    'author_email': 'alex.sansone@cybergrx.com',
    'url': 'https://github.com/CyberGRX/marshmallow-sqlalchemy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
