"""
Emulates a Travis CI run
"""
import candig.common
import candig.common.cli as cli
import candig.common.utils as utils


class TravisSimulator(object):

    logStrPrefix = '***'
    yamlFileLocation = '.travis.yml'

    def parseTestCommands(self):
        yamlData = utils.getYamlDocument(self.yamlFileLocation)
        return yamlData['script']

    def runTests(self):
        testCommands = self.parseTestCommands()
        for command in testCommands:
            self.log('Running: "{}"'.format(command))
            utils.runCommand(command)
        self.log('SUCCESS')

    def log(self, logStr):
        utils.log("{0} {1}".format(self.logStrPrefix, logStr))


def run_tests_main():
    parser = cli.createArgumentParser("runs tests for a candig package")
    versionString = "CanDIG Runtests Version {}".format(
        candig.common.__version__)
    parser.add_argument(
        "--version", version=versionString, action="version")
    parser.parse_args()

    travisSimulator = TravisSimulator()
    travisSimulator.runTests()
