# coding: utf-8
from __future__ import absolute_import

import os

from . import settings as st


class OOWrapperException(Exception):
    pass


class OOWrapper(object):
    u"""
    Для работы с OpenOffice
    """

    def __init__(self, port=st.DEFAULT_OPENOFFICE_PORT):

        # 5.10.12. Вахотин. Если в проекте используется приложение(внесено в INSTALLED_APPS), которое
        # в свою очередь использует simple_report(например конструктор), то из-за uno не будут работать некоторые
        # команды manage.py (http://www.co-ment.org/ticket/29, https://code.djangoproject.com/ticket/11098)
        import uno
        from com.sun.star.beans import PropertyValue
        from com.sun.star.task import ErrorCodeIOException
        from com.sun.star.connection import NoConnectException
        self.uno = uno
        self.PropertyValue = PropertyValue
        self.ErrorCodeIOException = ErrorCodeIOException
        self.NoConnectException = NoConnectException

        localContext = self.uno.getComponentContext()
        resolver = localContext.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver",
            localContext)
        try:
            context = resolver.resolve("uno:socket,host=localhost,port=%s;urp;StarOffice.ComponentContext" % port)
        except self.NoConnectException:
            raise OOWrapperException("failed to connect to OpenOffice.org on port %s" % port)
        self.desktop = context.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", context)

    def convert(self, inputFile, _outputExt, outputFile=None):
        """
        """

        if not outputFile:
            outputFile, _ = os.path.splitext(inputFile)
            outputFile = os.path.extsep.join((outputFile, _outputExt))

        inputUrl = self._toFileUrl(inputFile)
        outputUrl = self._toFileUrl(outputFile)

        loadProperties = {"Hidden": True}
        inputExt = self._getFileExt(inputFile)
        if inputExt in st.IMPORT_FILTER_MAP:
            loadProperties.update(st.IMPORT_FILTER_MAP[inputExt])

        document = self.desktop.loadComponentFromURL(inputUrl, "_blank", 0,
            self._toProperties(loadProperties))
        try:
            document.refresh()
        except AttributeError:
            pass

        family = self._detectFamily(document)
        self._overridePageStyleProperties(document, family)

        outputExt = self._getFileExt(outputFile)
        storeProperties = self._getStoreProperties(document, outputExt)

        try:
            document.storeToURL(outputUrl, self._toProperties(storeProperties))
        finally:
            document.close(True)

        return self.uno.fileUrlToSystemPath(outputUrl)

    def _overridePageStyleProperties(self, document, family):
        """
        """
        if family in st.PAGE_STYLE_OVERRIDE_PROPERTIES:
            properties = st.PAGE_STYLE_OVERRIDE_PROPERTIES[family]
            pageStyles = document.getStyleFamilies().getByName('PageStyles')
            for styleName in pageStyles.getElementNames():
                pageStyle = pageStyles.getByName(styleName)
                for name, value in properties.items():
                    pageStyle.setPropertyValue(name, value)

    def _getStoreProperties(self, document, outputExt):
        family = self._detectFamily(document)
        try:
            propertiesByFamily = st.EXPORT_FILTER_MAP[outputExt]
        except KeyError:
            raise OOWrapperException("unknown output format: '%s'" % outputExt)
        try:
            return propertiesByFamily[family]
        except KeyError:
            raise OOWrapperException("unsupported conversion: from '%s' to '%s'" % (family, outputExt))

    def _detectFamily(self, document):
        if document.supportsService("com.sun.star.text.WebDocument"):
            return st.FAMILY_WEB
        if document.supportsService("com.sun.star.text.GenericTextDocument"):
            # must be TextDocument or GlobalDocument
            return st.FAMILY_TEXT
        if document.supportsService("com.sun.star.sheet.SpreadsheetDocument"):
            return st.FAMILY_SPREADSHEET
        if document.supportsService("com.sun.star.presentation.PresentationDocument"):
            return st.FAMILY_PRESENTATION
        if document.supportsService("com.sun.star.drawing.DrawingDocument"):
            return st.FAMILY_DRAWING
        raise OOWrapperException("unknown document family: %s" % document)

    def _getFileExt(self, path):
        ext = os.path.splitext(path)[1]
        if ext is not None:
            return ext[1:].lower()

    def _toFileUrl(self, path):

        return self.uno.systemPathToFileUrl(os.path.abspath(path))

    def _toProperties(self, dict):
        props = []
        for key in dict:
            prop = self.PropertyValue()
            prop.Name = key
            prop.Value = dict[key]
            props.append(prop)
        return tuple(props)
