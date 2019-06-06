#! /usr/bin/env python
# encoding: utf-8
from __future__ import absolute_import, division, print_function

from datetime import datetime

from sqlalchemy.orm import sessionmaker

from .errors import InvalidOperationError
from .instance.db_objects import CommentDbo, SignalCommentAssociation, SignalDbo

# Copyright © 2018 Uwe Schmitt <uwe.schmitt@id.ethz.ch>


def add_comment(engine, signal_id, text, author, comment_id=None):

    session = sessionmaker(bind=engine)()

    if not session.query(SignalDbo).filter(SignalDbo.signal_id == signal_id).count():
        raise InvalidOperationError(
            "no signal with id {} in database".format(signal_id)
        )

    comment_dbo = CommentDbo(
        text=text, author=author, timestamp=datetime(1971, 4, 8), comment_id=comment_id
    )
    association_dbo = SignalCommentAssociation()
    association_dbo.signal_id = signal_id
    association_dbo.comment = comment_dbo
    session.add(comment_dbo)
    session.add(association_dbo)
    session.commit()
    return comment_dbo


def delete_comment(engine, comment_id):
    session = sessionmaker(bind=engine)()
    comments = (
        session.query(CommentDbo).filter(CommentDbo.comment_id == comment_id).all()
    )
    if not comments:
        raise InvalidOperationError("no comment with id {} in db".format(comment_id))
    assert len(comments) == 1

    associations = (
        session.query(SignalCommentAssociation)
        .filter(SignalCommentAssociation.comment_id == comment_id)
        .all()
    )
    session.delete(comments[0])
    for association in associations:
        session.delete(association)
    session.commit()
