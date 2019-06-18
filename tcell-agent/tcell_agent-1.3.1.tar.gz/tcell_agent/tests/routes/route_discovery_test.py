import unittest

from mock import Mock, patch

from tcell_agent.routes.route_discovery import RouteTable


class RouteDiscoveryTest(unittest.TestCase):
    def test_simple_database_route(self):
        events_seen = []

        def send_event_func(event):
            events_seen.append(event)

        logger = Mock()
        with patch("tcell_agent.routes.route_discovery.get_module_logger", return_value=logger):
            with patch.object(logger, "info") as patched_info:
                route_table = RouteTable()
                self.assertTrue(patched_info.called)
                args, _ = patched_info.call_args
                self.assertEqual(args, ("Initializing route table.",))

                route_table.discover_database_fields("databasex", "schemax", "tablex", ["fieldx"], "routex", send_event_func)
                route_table.discover_database_fields("databasex", "schemax", "tablex", ["fieldx"], "routex", send_event_func)
                route_table.discover_database_fields("databasex", "schemax", "tablex", ["fieldx"], "routex", send_event_func)
                route_table.discover_database_fields("databasex", "schemax", "tablex", ["fieldx"], "routex", send_event_func)

                self.assertEqual(route_table.routes["routex"].database_fields[
                    hash("databasex,schemax,tablex," + ",".join(["fieldx"]))].discovered, True)
                self.assertEqual(route_table.routes["routex"].database_fields[
                    hash("databasex,schemax,tabley," + ",".join(["fieldx"]))].discovered, False)
                self.assertEqual(len(events_seen), 1)
