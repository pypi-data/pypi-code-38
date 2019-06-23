__author__ = 'synerty'

from twisted.cred.checkers import InMemoryUsernamePasswordDatabaseDontUse





authChecker = InMemoryUsernamePasswordDatabaseDontUse(joe='blow')