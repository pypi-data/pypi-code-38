import unittest

import strongr.clouddomain.model.gateways

import strongr.core
import strongr.core.domain.clouddomain

class TestIntraDomainEvent(unittest.TestCase):
    def test_salt_job_finished(self):
        intra_domain_event_factory = strongr.clouddomain.model.gateways.Gateways.intra_domain_event_factory()
        cloudService = strongr.core.domain.clouddomain.CloudDomain.cloudService() # this initializes event subscribers within the domain

        event = intra_domain_event_factory.newSaltJobFinished('1', 'Test return', 0)

        strongr.clouddomain.model.gateways.Gateways.intra_domain_events_publisher().subscribe(event.__class__,
            lambda event: self.assertTrue(True)
        )

        strongr.clouddomain.model.gateways.Gateways.intra_domain_events_publisher().publish(event)
