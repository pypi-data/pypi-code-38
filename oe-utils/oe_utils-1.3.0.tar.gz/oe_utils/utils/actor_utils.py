# -*- coding: utf-8 -*-

def actor_uri(user):
    actor = user.get("actor", {})
    return actor.get("uri", "NA")
