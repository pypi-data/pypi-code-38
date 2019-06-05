from strongr.configdomain.command import LoadConfig

from strongr.core.exception import InvalidParameterException

class CommandFactory:
    """ this factory instantiates command objects to be sent to a scheduler commandbus. """
    def newLoadConfig(self, environment):
        """ generates a new loadconfig command

        :param environment: the environment that should be loaded
        :type environment: string

        :returns: a loadconfig command object
        :rtype: loadconfig
        """
        if not len(environment) > 0:
            raise InvalidParameterException('environment is invalid')
        return LoadConfig(environment)
