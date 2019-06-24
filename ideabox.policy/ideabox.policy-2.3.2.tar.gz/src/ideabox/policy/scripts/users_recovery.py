# encoding: utf-8

from Zope2.App import startup
from plone import api
from plone.i18n.normalizer import urlnormalizer
from transaction import commit
from zope.component.hooks import setSite

import argparse
import csv
import password_generator


def add_user(author, mail):
    if len(author) < 3:
        author_id = urlnormalizer.normalize(mail[0:3].decode("utf8"), locale="fr")
    else:
        author_id = urlnormalizer.normalize(author.decode("utf8"), locale="fr")
    with api.env.adopt_user(username="admin"):
        if api.user.get(username=author_id) is None:
            pwd = password_generator.generate(length=20)
            user = api.user.create(
                username=author_id, email=mail, password="{0}1.".format(pwd)
            )
            user.setMemberProperties(mapping={"fullname": author})


def data_recovery(filename):
    csv_file = open(filename, "rb")
    reader = csv.reader(csv_file, delimiter=";")
    reader.next()
    for line in reader:
        author = line[3]
        author_mail = line[4]

        add_user(author, author_mail)


def main(app):
    startup.startup()

    parser = argparse.ArgumentParser()
    parser.add_argument("-c")
    parser.add_argument("csv", help="csv file")
    parser.add_argument("name", help="Name of plone site")
    args = parser.parse_args()

    setSite(app[args.name])

    if args.csv:
        data_recovery(args.csv)
        commit()


if "app" in locals():
    main(app)  # NOQA
