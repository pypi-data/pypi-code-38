"""
Read/Write data on xml file for very simple database


Args:
    xmlFile (str | pathlib.Path): xml file name or Path object

Raises:
    ValueError: Raised when the xml file can not be created
        when first run and the file still don't exist

Examples:

    db = XmlDB("/dir/data.xml")
    db.initXmlFile('Data', ['Group1', 'Group2'])

    # if the record exist it data is update
    attrib = {'type': 'type1', 'other': 'one'} # can be empty
    db.add('Group1', 'id1' , a, 'Record 1')

    attrib = {'type': 'type2', 'other': 'two'} # can be empty
    db.add('Group2', 'id1' , a, 'Record 2')

    data = db.get('Group1', 'id1')
    db.remove('Group2', 'id1')


    # search is done by attributes inclusive all have to match
    # no key is needed this two are enough to pick only one
    # record
    attrib = {'type': 'type1', 'other': 'one'}
    data = db.search(attrib)

    In the example the record id is the same but group+id is unique
    and the get uses the group

::

 xml format:

    <?xml version="1.0" ?>
    <Data>
        <Group1>
            <Record type='type1' other='one' recordID='id1' recordType='python-type'>Record 1</Record>
        </Group1>
        <Group2>
            <Record type='type2' other='one' recordID='id1' recordType='python-type'>Record 2</Record>
        </Group2>
    </Data>

    recordType can be:

        - bool, byes, numbers: int, float, complex, strings
        - and dictionaries, lists and tuples of basic data types

    binary data that can converted to base64 and save as bytes
    can work the conversion from byres to binary is not
    manage by the class
"""

# XML0001


# pylint: disable=protected-access
# used for isinstance check


# standar imports
import ast
from pathlib import Path

# third-party imports
import lxml
import lxml.etree as ET


class XmlDB:
    """simple xml file database"""

    def __init__(self, xmlFile=None):

        self._xmlFile = None
        self._tree = None
        self._root = None
        self._status = None

        if xmlFile is not None:

            self.xmlFile = xmlFile

    def __bool__(self):

        return self._xmlFile is not None

    @property
    def root(self):
        """root of xml db"""
        return self._root

    @property
    def status(self):
        """Error message"""
        return self._status

    @property
    def xmlFileName(self):
        """xml file name string"""
        return str(self._xmlFile)

    @property
    def xmlDocPretty(self):
        """pretty printed xml document"""
        return ET.tostring(self._root, pretty_print=True).decode()

    @property
    def xmlFile(self):
        """xml file Path object"""
        return self._xmlFile

    @xmlFile.setter
    def xmlFile(self, xmlFile):
        """
        setup xml file paremeter can be a string or a Path
        """

        bError = False
        eMsg = ""

        if xmlFile is not None:

            if isinstance(xmlFile, Path):
                p = xmlFile
            else:
                p = Path(xmlFile)

            if not p.is_dir():
                if not p.is_file():
                    if p.parent.is_dir():
                        p.touch()

                if p.is_file():
                    self._xmlFile = p
                    if p.stat().st_size > 0:
                        self._openXmlFile()
                else:
                    eMsg = str(p) + " could not be created"
                    bError = True
            else:
                eMsg = str(p) + " is a directory is an error"
                bError = True
        else:
            eMsg = "File parameter is None"
            bError = True

        if bError:
            self._xmlFile = None
            self._status = eMsg
            raise ValueError(eMsg)

    def initXmlFile(self, root, groups, force=False):
        """init the xml file if empty force=True do clear"""

        if self._xmlFile is not None:

            size = self._xmlFile.stat().st_size

            if not size or force:
                r = ET.Element(root)

                for tag in groups:
                    ET.SubElement(r, tag)

                e = ET.SubElement(r, Key.InitializationValues)
                cfg = ET.SubElement(e, 'FileRoot')
                cfg.text = root
                cfg = ET.SubElement(e, 'Groups')
                cfg.text = str(groups)

                tree = ET.ElementTree(r)

                tree.write(self.xmlFileName)

                self._status = "File initialized."
            else:
                self._status = "File already initialized.\nUse force=True to reinitialized (WARNING! all records are purged)"

            self._openXmlFile()

        else:

            raise RuntimeError("XML file not defined.")

    def _openXmlFile(self):
        """open xml file"""

        if self._xmlFile is not None:

            #try: lxml.etree.XMLSyntaxError
            #TypeError
            try:
                self._tree = ET.parse(self.xmlFileName)
                self._root = self._tree.getroot()
            except lxml.etree.XMLSyntaxError as error:
                self._status = "Error on file {} - {} ".format(
                    self.xmlFileName,
                    error.msg
                )
            except TypeError as error:
                self._status = str(error.args)

    def add(self, group, recordID, attrib, data):
        """add record to xml group"""

        r = self._root
        attr = attrib

        if not isinstance(recordID, str):
            strID = str(recordID)
        else:
            strID = recordID

        attr[Key.recordID] = strID
        attr[Key.recordType] = type(data).__name__

        ge = r.find('.//' + group) # group to actualize

        if isinstance(ge, ET._Element):

            # search record
            find = ET.XPath('.//' + group + '/' + 'Record[@recordID="' + str(recordID) + '"]')
            try:
                e = find(r)[0]
            except IndexError:
                e = None

            if isinstance(e, ET._Element):
                e.text = str(data)
            else:
                e = ET.SubElement(ge, "Record")
                for key in attr:
                    e.set(key, attr[key])
                e.text = str(data)

            self._tree.write(self.xmlFileName)

            self._status = "Record added"
        else:
            self._status = "Group not found: group - {}".format(
                group
            )

    def get(self, group, recordID):
        """get record"""

        if not isinstance(recordID, str):
            strID = str(recordID)
        else:
            strID = recordID

        value = None

        r = self._root

        # search record
        find = ET.XPath('.//' + group + '/' + 'Record[@recordID="' + strID + '"]')

        try:
            e = find(r)[0]
        except IndexError:
            e = None

        if isinstance(e, ET._Element):

            if e.attrib[Key.recordType] == "str":
                value = e.text
            else:
                value = ast.literal_eval(e.text)

            self._status = "Get record successful"

        else:
            self._status = "Record not found: group - {} record id - {}".format(
                group,
                strID
            )

        return value

    def getGroupRoot(self, group):
        """returns the root of a group"""

        r = self._root
        find = ET.XPath('.//' + group)

        try:
            e = find(r)[0]
        except IndexError:
            e = None

        return e

    def remove(self, group, recordID):
        """add record to xml group"""

        if not isinstance(recordID, str):
            strID = str(recordID)
        else:
            strID = recordID

        r = self._root

        # search record
        find = ET.XPath('.//' + group + '/' + 'Record[@id="' + strID + '"]')
        try:
            e = find(r)[0]
        except IndexError:
            e = None

        if isinstance(e, ET._Element):
            # get parent of record then remove from parent
            p = e.getparent()
            p.remove(e)

            self._tree.write(self.xmlFileName)

            self._status = "Remove successful"
            return True
        else:
            self._status = "Record to remove not found: group - {} record id - {}".format(
                group,
                strID
            )
        return False

    def search(self, attrib):
        """add record to xml group
        [contains(@name, "Jack Reacher") and contains(@date, "2016") and contains(@type, "Movie")]
        """

        value = None
        if not isinstance(attrib, dict):
            return None

        r = self._root
        sa = _attribToString(attrib)
        find = ET.XPath('.//Record' + sa)

        try:
            s = find(r)[0]
        except IndexError:
            s = None
        except TypeError:
            s = None

        if isinstance(s, ET._Element):
            if s.attrib[Key.recordType] == "str":
                value = s.text
            else:
                value = ast.literal_eval(s.text)
            self._status = "Last search successful"
        else:
            self._status = "Last search failed: " + str(attrib)


        return value


class Key:
    """Dictionary keys"""

    recordID = "recordID"
    recordType = "recordType"
    InitializationValues = "InitializationValues"
    Movie = "Movie"
    TV = "TV"

def _attribToString(attrib):
    """
    convert attrib dictionnary to string suitable for XPath search

    {'name': 'Reacher', 'date': '2016', 'type': 'Movie'}
    [contains(@name, "Reacher") and contains(@type, "Movie")]
    """

    s = "["

    lFirst = True

    for k in attrib:
        if lFirst:
            s = s + "contains(@" + k + ', "' + attrib[k] + '")'
            lFirst = False
        else:
            s = s + " and contains(@" + k + ', "' + attrib[k] + '")'

    s = s + "]"

    return s
