import logging
from .base import MUDInterface

class HelpInterface(MUDInterface):

    name = "help"

    def help_lookup(self, requested_topic):
        requested_topic = requested_topic.lower()
        for topic, help in sorted(Help._known_help.items(), key=lambda x: f"{x[1].sort_order*-1}_{x[0]}"):
            if topic.lower() == requested_topic.lower() or topic.lower().startswith(requested_topic.lower()):
                return help
        return None

    def default_help(self):

        msg = ""

        for classification in sorted(Help._classifications.keys()):
            msg += f"{classification.upper()}\r\n"
            msg += "\r\n".join(sorted(Help._classifications[classification].keys())) + "\r\n\r\n"

        return msg

class Help(object):

    _known_help = {}
    _classifications = {}

    def __init__(self, topic, details, classification="", sort_order=0):

        topic = topic.lower()

        self.topic = topic
        self.details = details
        self.sort_order = sort_order
        self.classification = classification

        if classification and classification not in Help._classifications:
            if classification in Help._known_help or classification == topic:
                logging.warning(f"Classification {classification} is already a help topic, will clobber results when looking up help")
            Help._classifications[classification] = {}

        if topic in Help._known_help:
            prev_help = Help._known_help[topic]
            prev_class = prev_help.classification
            if prev_class in Help._classifications:
                del Help._classifications[prev_class][topic]
            logging.info(f"Replacing existing help topic f{topic}")

        Help._known_help[topic] = self
        if classification:
            Help._classifications[classification][topic] = self

    def set_classification(self, classification):

        if self.classification and self.classification in Help._classifications:
            del Help._classifications[self.classification][self.topic]

        self.classification = classification
        if classification not in Help._classifications:
            Help._classifications[classification] = {}
        Help._classifications[classification][self.topic] = self

