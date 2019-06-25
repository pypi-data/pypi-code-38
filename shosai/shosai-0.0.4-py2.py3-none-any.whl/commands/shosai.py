import sys
import typing as t
import os.path
import json
import logging
import re  # xxx
from shosai.langhelpers import NameStore

logger = logging.getLogger(__name__)


def search(
    service: str,
    *,
    config_path: str,
    mapping_path: str,
    save: bool = False,
    show_mapping: bool = False,
    query: t.Optional[str] = None,
    page: t.Optional[int] = None,
    per_page: t.Optional[int] = None,
    out: t.Optional[t.IO] = None,
    verbose: bool = False,
) -> None:
    from shosai import App

    out = out or sys.stdout
    app = App(config_path, service=service, mapping_path=mapping_path)
    with app.resource as r:
        data = r.search(q=query, page=page, per_page=per_page)
    if show_mapping:
        for _, mapping in app.transform.from_search_response(data):
            json.dump(mapping, out, indent=2, ensure_ascii=False)
            out.write(os.linesep)
    else:
        json.dump(data, out, indent=2, ensure_ascii=False)
    if save:
        with app.saver as append:
            for post, mapping in app.transform.from_search_response(data):
                append(post, mapping, savefile=True)  # xxx


def clone(
    service: str,
    *,
    config_path: str,
    mapping_path: str,
    url: str,
    name: t.Optional[str] = None,
    out: t.Optional[t.IO] = None,
    verbose: bool = False,
) -> None:
    from shosai import App

    out = out or sys.stdout
    app = App(config_path, service=service, mapping_path=mapping_path)
    with app.resource as r:
        data = r.fetch.from_url(url)
    with app.saver as append:
        post, mapping = app.transform.from_fetch_response(data)
        append(post, mapping, name=name, savefile=True)


def pull(
    service: str,
    *,
    config_path: str,
    mapping_path: str,
    path: str,
    out: t.Optional[t.IO] = None,
    verbose: bool = False,
) -> None:
    from shosai import App

    out = out or sys.stdout
    app = App(config_path, service=service, mapping_path=mapping_path)
    with app.resource as r:
        meta = app.loader.lookup(path)
        if meta is None:
            print(f"mapped file is not found {path}", file=sys.stderr)
            sys.exit(1)
        data = r.fetch(meta["id"])
    with app.saver as append:
        post, mapping = app.transform.from_fetch_response(data)
        append(post, mapping, filepath=meta["file"], savefile=True)


def push(
    service: str,
    *,
    config_path: str,
    mapping_path: str,
    save: bool = True,
    path: str,
    draft: t.Optional[bool] = None,
    notice: bool = False,
    id: t.Optional[str] = None,
    out: t.Optional[t.IO] = None,
    verbose: bool = False,
) -> None:
    from shosai import App
    from shosai import parsing

    out = out or sys.stdout
    app = App(config_path, service=service, mapping_path=mapping_path)
    with app.resource as r:
        with open(path) as rf:
            parsed = parsing.parse_article(rf.read())

        meta = app.loader.lookup(path)
        id = id or (meta and meta["id"])

        # parse article and upload images as attachments.
        attachments = []
        namestore = NameStore()
        content = parsed.content

        for image in parsed.images:
            if "://" in image.src:
                continue
            imagepath = os.path.expanduser(
                os.path.join(os.path.dirname(path), image.src).strip("'").strip('"')
            )
            if not os.path.exists(imagepath):
                logger.info("image: %s is not found (where %s)", imagepath, path)
                continue
            if image.src in namestore:
                continue
            namestore[image.src] = os.path.basename(imagepath)
            attachments.append(
                r.attachment.build_content_from_file(
                    imagepath, name=namestore[image.src]
                )
            )
        if attachments:
            logger.info("attachments is found, the length is %d", len(attachments))
            uploaded = r.attachment(attachments)

            logger.info("overwrite passed article %s", path)
            for uploaded_image in uploaded:
                image_src = namestore.reverse_lookup(uploaded_image["name"])
                rx = re.compile(f"\\( *{image_src}*\\)")
                content = rx.subn(f"({uploaded_image['url']})", content)[0]
            with open(path, "w") as wf:
                tagspart = "".join([f"[{t}]" for t in parsed.tags])
                wf.write(f"#{tagspart}{parsed.title}\n")
                wf.write("")
                wf.write(content)

        data = r.post(
            parsed.title or (meta and meta.get("title")) or "",
            content,
            tags=parsed.tags,
            id=id,
            draft=draft,
            notice=notice,
            meta=meta,
        )
    if verbose:
        json.dump(data, out, indent=2, ensure_ascii=False)
    if save:
        with app.saver as append:
            post, mapping = app.transform.from_fetch_response(data)
            append(post, mapping, filepath=path, savefile=False)


def main(argv: t.Optional[t.Sequence[str]] = None) -> None:
    import argparse

    parser = argparse.ArgumentParser(description=None, add_help=False)
    subparsers = parser.add_subparsers(required=True, dest="service")

    service = "docbase"
    sparser = subparsers.add_parser(
        service, description=f"shosai for {service}", add_help=False
    )
    sparser.set_defaults(service=service)

    service = "hatena"
    sparser = subparsers.add_parser(
        service, description=f"shosai for {service}", add_help=False
    )
    sparser.set_defaults(service=service)

    args, rest_argv = parser.parse_known_args(argv)
    return submain(args.service, rest_argv)


def submain(service: str, argv: t.Optional[t.Sequence[str]] = None) -> None:
    import argparse

    parser = argparse.ArgumentParser(description=None)
    parser.print_usage = parser.print_help  # hack
    parser.add_argument(
        "--logging",
        default="INFO",
        choices=list(logging._nameToLevel.keys()),
        dest="log",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    subparsers = parser.add_subparsers(required=True, dest="subcommand")

    # search
    fn = search
    sparser = subparsers.add_parser(fn.__name__, description=fn.__doc__)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("-c", "--config", required=False, dest="config_path")
    sparser.add_argument("--mapping", default=None, type=int, dest="mapping_path")
    sparser.add_argument("--save", action="store_true")
    sparser.add_argument("--show-mapping", action="store_true")
    sparser.add_argument("-q", "--query", default=None)
    sparser.add_argument("--page", default=None, type=int)
    sparser.add_argument("--per_page", default=None, type=int)

    # clone
    fn = clone
    sparser = subparsers.add_parser(fn.__name__, description=fn.__doc__)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("-c", "--config", required=False, dest="config_path")
    sparser.add_argument("--mapping", default=None, type=int, dest="mapping_path")
    sparser.add_argument("url")
    sparser.add_argument("--name")

    # pull
    fn = pull
    sparser = subparsers.add_parser(fn.__name__, description=fn.__doc__)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("-c", "--config", required=False, dest="config_path")
    sparser.add_argument("--mapping", default=None, type=int, dest="mapping_path")
    sparser.add_argument("path")

    # push
    fn = push
    sparser = subparsers.add_parser(fn.__name__, description=fn.__doc__)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("-c", "--config", required=False, dest="config_path")
    sparser.add_argument("--mapping", default=None, type=int, dest="mapping_path")
    sparser.add_argument("--unsave", action="store_false", dest="save")
    sparser.add_argument("path")
    sparser.add_argument("--publish", action="store_false", dest="draft", default=None)
    sparser.add_argument("--notice", action="store_true")
    sparser.add_argument("--id")

    args = parser.parse_args(argv)
    params = vars(args).copy()

    logging.basicConfig(level=getattr(logging, params.pop("log")), stream=sys.stderr)
    import requests

    try:
        return params.pop("subcommand")(service, **params)
    except requests.exceptions.HTTPError as e:
        logger.warn("%s -- %r", e, e.response.text)
        logger.debug(str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
