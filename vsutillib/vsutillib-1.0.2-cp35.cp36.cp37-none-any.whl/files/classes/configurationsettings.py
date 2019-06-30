"""
Class to save/restore configuration from file
"""

# CM0003

import ast
import base64
import logging
import pickle
import xml
import xml.etree.ElementTree as ET
import xml.dom.minidom as DOM

from pathlib import Path

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class ConfigurationSettings:
    """
    Maintains a dictionary that can be saved to an
    xml file. It can restore the values reading the
    file.

    Examples:

    .. code-block:: python

        >>> cfg = ConfigurationSettings('file.xml')
        >>> value = "Configuration Value"
        >>> value
        'Configuration Value'
        >>> cfg.set('key', value)
        >>> cfg.get('key')
        'Configuration Value'
        >>> cfg.saveToFile()
        >>> cfg2 = ConfigurationSettings('file.xml')
        >>> cfg2.readFromFile()
        >>> value2 = cfg2.get('key')
        >>> value2
        'Configuration Value'

    Next exmaple using a class

    .. code-block:: python

        >>> from vsutillib.files import ConfigurationSettings
        >>> class Abc():
        ...     def __init__(self, param):
        ...         self.value = param
        ...     def getValue(self):
        ...         return self.value
        ...
        >>> cfg = ConfigurationSettings('file.xml')
        >>> c = Abc(13)
        >>> c.getValue()
        13
        >>> cfg.set('class', c, valueType='pickle')
        >>> cfg.saveToFile()
        >>> cfg2 = ConfigurationSettings('file.xml')
        >>> cfg2.readFromFile()
        >>> c2 = cfg2.get('class')
        >>> c2.getValue()
        13

    keys have to be strings

    It works with basic data types:

        basic data types and lists, dictionaries,
        tuples or sets of these data types

        - bool, byes, numbers: [int, float, complex], strings, set

        theese types can be saved but not in lists, dictionaries,
        tuples or sets

        - range, bytearray, frozenset, function


    Binary data or lists, dictionaries, tuple and sets with
    binary data can be tried with **valueType='pickle'**.  As seen
    in the second example using a class is possible but it does not
    always work.  The scope of the class ConfigurationSettings is
    for saving simple items that serve as a configuration setting
    for an application in different operating systems. Is recommended
    not to use values that have to be pickled this will make it system
    dependent also it may be dependent of the Python version. That
    said binary values have to be througly tested.

    Args:
        configFile (str): xml file name or Path object

    Raises:
        ValueError: Raised when the xml file can not be created
                    when first run and the file still don't exist
    """

    # log state
    __log = False

    # data that can be treated as literal
    # theese are human readable easier
    # to use on different systems
    _literal = [
        'bool', 'bytes', 'complex', 'float', 'int', 'str', 'dict', 'list',
        'tuple', 'set'
    ]

    # pickable types are python specific maybe
    # even version specific
    _pickable = ['range', 'bytearray', 'frozenset', 'function', 'pickle']

    @classmethod
    def classLog(cls, setLogging=None):
        """
        get/set logging at class level
        every class instance will log
        unless overwritten

        Args:
            setLogging (bool):
                - True class will log
                - False turn off logging
                - None returns current Value

        Returns:
            bool:

            returns the current value set
        """

        if setLogging is not None:
            if isinstance(setLogging, bool):
                cls.__log = setLogging

        return cls.__log

    def __init__(self, configFile=None):

        self._config = {}
        self._configType = {}
        self._configFile = configFile

        # for iteration
        self._current = 0
        self._len = 0

        # global logging override
        self.__log = None

    def __contains__(self, value):
        return value in self._config

    def __getitem__(self, key):
        return self._config[key]

    def __setitem__(self, key, value):
        self._config[key] = value

    def __iter__(self):
        return self

    def __next__(self):
        if self._current >= self._len:
            self._current = 0
            raise StopIteration
        else:
            self._current += 1
            key = list(self._config)[self._current - 1]
            return [key, self._config[key]]

    def __bool__(self):
        return len(self._config)

    def __len__(self):
        return len(self._config)

    @property
    def log(self):
        """
        class property can be used to override the class global
        logging setting

        Returns:
            bool:

            True if logging is enable

            False otherwise
        """
        if self.__log is not None:
            return self.__log

        return ConfigurationSettings.classLog()

    @log.setter
    def log(self, value):
        """set instance log variable"""
        if isinstance(value, bool) or value is None:
            self.__log = value

    def set(self, key, value, valueType=None):
        """
        set value at key in dictionary

        Args:
            key (str): configuration element

            value: element value the type
            is as explained
        """

        if isinstance(key, str):

            self._config[key] = value
            _valueType = type(value).__name__

            if valueType is not None:
                _valueType = valueType

            if not ((_valueType in self._pickable) or
                    (_valueType in self._literal)):
                s = str(_valueType)
                if self.log:
                    MODULELOG.debug('CM0003: value type not supported - %s',
                                    str(s))
                raise TypeError('value type not supported - {}'.format(s))

            self._configType[key] = _valueType

            self._len = len(self._config)
        else:
            s = str(key)
            if self.log:
                MODULELOG.debug('CM0002: key must be a string - %s', str(s))
            raise TypeError('key must be a string - {}'.format(s))

    def get(self, key):
        """
        get value from dictionary

        Args:
            key (str): configuration element

        Returns:
            object as explained
        """

        if key in self._config:
            return self._config[key]

        if self.log:
            s = str(key)
            MODULELOG.debug('CM0001: key not found - %s', s)

        return None

    def toXML(self, root=None, name=None):
        """
        Returns the configuration in XML format
        if root is None returns the current configuration

        Args:
            root (xml.etree.ElementTree): root of document

            name (str): root tag

        Returns:
            xml.etree.ElementTree
        """

        if name is None:
            name = "Config"

        config = ET.Element(name)

        if root is not None:
            root.append(config)

        for key, value in self:
            valueType = type(value).__name__

            if key in self._configType:
                valueType = self._configType[key]

            if valueType in self._literal:
                tValue = value
            elif valueType in self._pickable:
                p = pickle.dumps(value)
                u = base64.b64encode(p)
                tValue = u

            configElement = ET.SubElement(config, 'ConfigSetting')
            configElement.attrib = {'id': key, 'type': valueType}
            configElement.text = str(tValue)

        if root is None:
            return config

        return root

    def fromXML(self, xmlDoc, name=None):
        """
        Restore configuration from xml name parameter
        permit various configuration sets on same
        xml document

        Args:
            xmlDoc (xml.etree.ElementTree): xml document containing
            configuration data
        """
        self._config = {}

        if name is None:
            searchIn = "Config/ConfigSetting"
        else:
            searchIn = name + "/ConfigSetting"

        for setting in xmlDoc.findall(searchIn):

            key = setting.attrib['id']
            valueType = setting.attrib['type']

            if valueType == "str":
                value = setting.text
            elif valueType in self._pickable:
                u = ast.literal_eval(setting.text)
                value = pickle.loads(base64.b64decode(u))
            else:
                value = ast.literal_eval(setting.text)

            self.set(key, value, valueType=valueType)

    def xmlPrettyPrint(self, root=None):
        """
        Returns configuration xml Pretty Printed

        Args:
            root (xml.etree.ElementTree)

        Returns:
            xml.dom.minidom
        """

        if root is not None:
            if not isinstance(root, xml.etree.ElementTree.Element):
                return None
        else:
            root = self.toXML()

        xmlDoc = DOM.parseString(ET.tostring(root))

        xmlPretty = xmlDoc.toprettyxml(indent='    ')

        return xmlPretty

    def setConfigFile(self, xmlFile):
        """
        sets the file for reading and writing to
        """

        p = Path(xmlFile)

        if not p.anchor:
            xf = Path(Path.home(), xmlFile)
        else:
            xf = p

        self._configFile = xf

    def saveToFile(self, xmlFile=None, rootName=None):
        """
        save configuration to file in xml format

        Args:
            xmlFile (Path|str): file to write to

            rootName (str): root tag
        """

        xf = xmlFile
        if xmlFile is None:
            xf = self._configFile

        if rootName is None:
            rootTag = "VergaraSoft"

        root = ET.Element(rootTag)

        xmlConfig = self.toXML(root)
        tree = ET.ElementTree(xmlConfig)
        tree.write(str(xf))

    def readFromFile(self, xmlFile=None):
        """
        save configuration to file in xml format

        Args:
            xmlFile (Path|str): file to read

            rootName (str): root tag

        Raises:
            ValueError: raised when file con not be read
        """

        xf = xmlFile
        if xmlFile is None:
            xf = self._configFile

        f = Path(xf)

        if f.is_file():
            tree = ET.ElementTree(file=str(xf))
            root = tree.getroot()

            self.fromXML(root)


class Abc():
    """Test class"""

    def __init__(self, param):
        self.value = param

    def getValue(self):
        """Test method"""
        return self.value


def print13():
    """function for testing"""
    print('Print from function = 13')


def test():
    """Testing read and write configuration to file"""

    classInstance = Abc(13)

    configFile = Path(Path.cwd(), 'configmanager.xml')

    configuration = ConfigurationSettings(configFile=configFile)

    b = b'Sanson'

    configuration.set('range', range(13))
    configuration.set('set', {'r', 'n', 'a', 'f', 'e', 'i'})
    configuration.set('bytearray', bytearray(b'Itsue'))
    configuration.set('frozenset', frozenset('Itsue'))
    configuration.set('function', print13, valueType='pickle')
    configuration.set('class', classInstance, valueType='pickle')
    configuration.set('bool', True)
    configuration.set(
        'base64sting',
        'AdnQywACAAAAAAHmAAAAoAAACM4AAAR5AAAB7wAAAMYAAAjFAAAEcAAAAAAAAAAACgA=')
    configuration.set(
        'base86bytes',
        'AdnQywACAAAAAAHmAAAAoAAACM4AAAR5AAAB7wAAAMYAAAjFAAAEcAAAAAAAAAAACgA='.
        encode())
    configuration.set('dict', {'key1': 1, 'key2': 2, 3: b})
    configuration.set('list', [2, 3, 'list', {
        'key1': 1,
        2: [2]
    }],
                      valueType='pickle')
    configuration.set('int', 13)
    configuration.set('float', 1.3e200)
    configuration.set('complex', 1 + 3j)
    configuration.set('tuple', (1.11, 2.22, 3.33))

    print('\nConfiguration set\n')
    for key, value in configuration:
        print('Key = {0}, type = {2} value = {1}'.format(
            key, value,
            type(value).__name__))

    configuration.saveToFile()

    configuration.readFromFile()

    root = configuration.toXML()

    print('\nRead from configuration file\n')
    for key, value in configuration:
        print('Key = {0}, type = {2}, value = {1}'.format(
            key, value,
            type(value).__name__))

    prettyXML = configuration.xmlPrettyPrint(root)

    print()
    print(prettyXML)
    print('Call function: ')
    f = configuration.get('function')
    f()
    c = configuration.get('class')
    print('Calling class method = {} '.format(c.getValue()))


if __name__ == "__main__":
    test()
