from .context import metamodel as mm

from hypothesis import given, settings
from hypothesis.strategies import composite, text, lists, floats, sampled_from

import unittest

NAME_ALPHABET = "abcdefghijklmnopqrstuvwxyz"

@composite
def ros_name(draw):
    return mm.RosName(draw(text(alphabet=NAME_ALPHABET, min_size=1)))

@composite
def node_instance(draw, config=None):
    return mm.NodeInstance(config, draw(ros_name()), None)

@composite
def ros_topic(draw, config=None):
    t = draw(text(alphabet=NAME_ALPHABET, min_size=1))
    return mm.Topic(config, draw(ros_name()), message_type=t)


@composite
def ros_config(draw):
    name = draw(text(alphabet=NAME_ALPHABET, min_size=1))
    config = mm.Configuration(name)
    topics = draw(lists(elements=ros_topic(config=config), min_size=1, unique=True))
    nodes = draw(lists(elements=node_instance(config=config), min_size=1, unique=True))
    _connect_nodes(draw, nodes, topics)
    for node in nodes:
        config.nodes.add(node)
    for topic in topics:
        config.topics.add(topic)
    return config


def _connect_nodes(draw, nodes, topics):
    for i in xrange(len(nodes)):
        ni = nodes[i]
        for j in xrange(i, len(nodes)):
            nj = nodes[j]
            p = draw(floats(min_value=0.0, max_value=1.0))
            if p <= 0.5:
                t = draw(sampled_from(topics))
                mm.PublishLink.link(ni, t, t.type, t.rosname, 10)
                mm.SubscribeLink.link(nj, t, t.type, t.rosname, 10)


class TestRTOutlinks(unittest.TestCase):
    @given(ros_config())
    @settings(deadline=None)
    def test_node_rt_outlinks(self, config):
        for node in config.nodes:
            links = node.rt_outlinks
            self.assertIn(node, links)
            for topic in config.topics:
                for pub in topic.publishers:
                    if node == pub.node:
                        for sub in topic.subscribers:
                            self.assertIn(sub.node, links)

if __name__ == '__main__':
    unittest.main()
