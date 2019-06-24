# encoding: utf-8

from Zope2.App import startup
from cioppino.twothumbs import rate
from plone import api
from plone.i18n.normalizer import urlnormalizer
from plone.namedfile.file import NamedBlobImage
from transaction import commit
from zope.component.hooks import setSite

import argparse
import csv
import os

from ideabox.policy.utils import token_type_recovery


def add_project(
    container,
    project_id,
    title,
    project_theme,
    project_body,
    image_source,
    project_author,
    project_like,
    project_unlike,
    project_status,
):
    img_extensions = ("jpg", "png", "gif")
    with api.env.adopt_user(username="admin"):
        project = api.content.create(
            type="Project",
            title=title,
            project_theme=project_theme,
            body=u"<br>".join(project_body.decode("utf8").splitlines()),
            container=container,
            original_author=project_author,
            original_id=project_id,
        )
        for ext in img_extensions:
            filename = "{0}.{1}".format(project_id, ext)
            img_path = os.path.join(image_source, filename)
            if os.path.exists(img_path):
                add_image_from_file(project, filename, image_source)
                break

    rate.setupAnnotations(project)
    if project_like:
        for x in range(0, int(project_like)):
            rate.loveIt(project, "userimportp" + str(x))
    if project_unlike:
        for x in range(0, int(project_unlike)):
            rate.hateIt(project, "userimportn" + str(x))

    with api.env.adopt_user(username="admin"):
        if project_status in ["selected", "rejected"]:
            api.content.transition(obj=project, transition="deposit")
            api.content.transition(obj=project, transition="to_be_analysed")
            api.content.transition(obj=project, transition="vote")
            api.content.transition(obj=project, transition="vote_analysis")
            if project_status == "selected":
                api.content.transition(obj=project, transition="accept")
            else:
                api.content.transition(obj=project, transition="reject")


def add_image_from_file(container, file_name, source):
    file_path = os.path.join(source, file_name)
    if not container.hasObject(file_name):
        # with deterity image
        named_blob_image = NamedBlobImage(
            data=open(file_path, "r").read(), filename=unicode(file_name)
        )
        image = api.content.create(
            type="Image",
            title=file_name,
            image=named_blob_image,
            container=container,
            language="fr",
        )
        image.setTitle(file_name)
        image.reindexObject()


def data_recovery(filename, image, container, status):
    csv_file = open(filename, "rb")
    reader = csv.reader(csv_file, delimiter=";")
    reader.next()
    for line in reader:
        project_id = line[0]
        project_title = line[2]
        project_theme = line[1]
        project_body = line[18]
        project_author = line[3]
        project_mail = line[4]
        project_like = line[15]
        project_unlike = line[16]

        token_type = token_type_recovery(project_theme)

        if len(project_author) < 3:
            project_author = urlnormalizer.normalize(
                project_mail[0:3].decode("utf8"), locale="fr"
            )
        else:
            project_author = urlnormalizer.normalize(
                project_author.decode("utf8"), locale="fr"
            )

        add_project(
            container,
            project_id,
            project_title,
            token_type,
            project_body,
            image,
            project_author,
            project_like,
            project_unlike,
            status,
        )
        print(project_title)


def follow_path(portal, path):
    element = portal
    for id in path.split("/"):
        if id not in element:
            raise ValueError("The id {0} does not exist".format(id))
        element = element[id]
    return element


def main(app):
    startup.startup()

    parser = argparse.ArgumentParser()
    parser.add_argument("-c")
    parser.add_argument("csv", help="csv file")
    parser.add_argument("img", help="localisation of pictures")
    parser.add_argument("name", help="Name of plone site")
    parser.add_argument("status", help="status of types")
    parser.add_argument("--path", dest="path", default="projets", help="creation path")
    args = parser.parse_args()

    setSite(app[args.name])
    portal = app[args.name]
    container = follow_path(portal, args.path)

    if args.csv and args.img:
        data_recovery(args.csv, args.img, container, args.status)
        commit()


if "app" in locals():
    main(app)  # NOQA
