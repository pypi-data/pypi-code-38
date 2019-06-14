from mock import patch, Mock

import pytest

from odcs.server import conf
from odcs.server.celery_tasks import TaskRouter


class TestCeleryRouter():

    @patch("odcs.server.celery_tasks.get_odcs_compose")
    def test_empty_rule(self, mock_get_compose):
        mock_compose = Mock()

        compose_md = {
            "source_type": 3
        }

        mock_conf = {
            "routing_rules": {
                "odcs.server.celery_tasks.generate_pungi_compose": {
                    "pungi_composes": {},
                    "other_composes": {
                        "source_type": 4,
                    },
                },
            },
            "cleanup_task": "odcs.server.celery_tasks.run_cleanup",
            "default_queue": "default_queue",
        }

        tr = TaskRouter()
        tr.config = mock_conf

        mock_compose.json.return_value = compose_md
        mock_get_compose.return_value = mock_compose
        args = [[1], {}]
        kwargs = {}
        queue = tr.route_for_task("odcs.server.celery_tasks.generate_pungi_compose",
                                  *args, **kwargs)
        assert queue == {"queue": "pungi_composes"}

    @patch("odcs.server.celery_tasks.get_odcs_compose")
    def test_default_queue(self, mock_get_compose):
        mock_compose = Mock()

        compose_md = {
            "source_type": 3
        }

        mock_conf = {
            "routing_rules": {
                "some.other.task": {
                    "pungi_composes": {},
                    "other_composes": {
                        "source_type": 4,
                    },
                },
            },
            "cleanup_task": "odcs.server.celery_tasks.run_cleanup",
            "default_queue": "default_queue",
        }

        tr = TaskRouter()
        tr.config = mock_conf

        mock_compose.json.return_value = compose_md
        mock_get_compose.return_value = mock_compose
        args = [[1], {}]
        kwargs = {}
        queue = tr.route_for_task("odcs.server.celery_tasks.generate_pungi_compose",
                                  *args, **kwargs)
        assert queue == {"queue": "default_queue"}

    @patch("odcs.server.celery_tasks.get_odcs_compose")
    def test_rule_with_single_property(self, mock_get_compose):
        mock_compose = Mock()

        compose_md = {
            "source_type": 3
        }

        mock_conf = {
            "routing_rules": {
                "odcs.server.celery_tasks.generate_pungi_compose": {
                    "pungi_composes": {
                        "source_type": 3,
                    },
                    "other_composes": {
                        "source_type": 4,
                    },
                },
            },
            "cleanup_task": "odcs.server.celery_tasks.run_cleanup",
            "default_queue": "default_queue",
        }

        tr = TaskRouter()
        tr.config = mock_conf

        mock_compose.json.return_value = compose_md
        mock_get_compose.return_value = mock_compose
        args = [[1], {}]
        kwargs = {}
        queue = tr.route_for_task("odcs.server.celery_tasks.generate_pungi_compose",
                                  *args, **kwargs)
        assert queue == {"queue": "pungi_composes"}

    @patch("odcs.server.celery_tasks.get_odcs_compose")
    def test_rule_with_list_property(self, mock_get_compose):
        mock_compose = Mock()

        compose_md = {
            "source_type": 3,
            "user": "mprahl",
        }

        mock_conf = {
            "routing_rules": {
                "odcs.server.celery_tasks.generate_pungi_compose": {
                    "pungi_composes": {
                        "source_type": 3,
                        "user": ["mcurlej", "jkaluza"],
                    },
                    "other_composes": {
                        "source_type": 3,
                        "user": ["mprahl", "lucarval"],
                    },
                },
            },
            "cleanup_task": "odcs.server.celery_tasks.run_cleanup",
            "default_queue": "default_queue",
        }

        tr = TaskRouter()
        tr.config = mock_conf

        mock_compose.json.return_value = compose_md
        mock_get_compose.return_value = mock_compose
        args = [[1], {}]
        kwargs = {}
        queue = tr.route_for_task("odcs.server.celery_tasks.generate_pungi_compose",
                                  *args, **kwargs)
        assert queue == {"queue": "other_composes"}

    @patch("odcs.server.celery_tasks.get_odcs_compose")
    def test_cleanup_queue(self, mock_get_compose):
        mock_compose = Mock()

        compose_md = {
            "source_type": 3
        }

        mock_conf = {
            "routing_rules": {
                "odcs.server.celery_tasks.generate_pungi_compose": {
                    "pungi_composes": {
                        "source_type": 3,
                    },
                    "other_composes": {
                        "source_type": 4,
                    },
                },
            },
            "cleanup_task": "odcs.server.celery_tasks.run_cleanup",
            "default_queue": "default_queue",
        }

        tr = TaskRouter()
        tr.config = mock_conf

        mock_compose.json.return_value = compose_md
        mock_get_compose.return_value = mock_compose
        args = [[1], {}]
        kwargs = {}
        queue = tr.route_for_task("odcs.server.celery_tasks.run_cleanup",
                                  *args, **kwargs)
        assert queue == {"queue": conf.celery_cleanup_queue}

    @patch("odcs.server.celery_tasks.get_odcs_compose")
    def test_invalid_rule_property_exception(self, mock_get_compose):
        mock_compose = Mock()

        compose_md = {
            "source_type": 3
        }

        mock_conf = {
            "routing_rules": {
                "odcs.server.celery_tasks.generate_pungi_compose": {
                    "pungi_composes": {
                        "bad_compose_prop": 3,
                    },
                },
            },
            "cleanup_task": "odcs.server.celery_tasks.run_cleanup",
            "default_queue": "default_queue",
        }

        tr = TaskRouter()
        tr.config = mock_conf

        mock_compose.json.return_value = compose_md
        mock_get_compose.return_value = mock_compose
        args = [[1], {}]
        kwargs = {}
        with pytest.raises(ValueError) as e:
            tr.route_for_task("odcs.server.celery_tasks.generate_pungi_compose",
                              *args, **kwargs)
            assert "invalid property" in e.args[0]
            assert "bad_compose_prop" in e.args[0]
