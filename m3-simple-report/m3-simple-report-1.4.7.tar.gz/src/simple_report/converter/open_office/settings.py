# coding: utf-8
DEFAULT_OPENOFFICE_PORT = 8100

FAMILY_TEXT = "Text"
FAMILY_WEB = "Web"
FAMILY_SPREADSHEET = "Spreadsheet"
FAMILY_PRESENTATION = "Presentation"
FAMILY_DRAWING = "Drawing"

IMPORT_FILTER_MAP = {
    "txt": {
        "FilterName": "Text (encoded)",
        "FilterOptions": "utf8"
    },
    "csv": {
        "FilterName": "Text - txt - csv (StarCalc)",
        "FilterOptions": "44,34,0"
    },
    "xls": {
        "FilterName": "MS Excel 97",
    },
    "doc": {
        "FilterName": "MS Word 97",
    },
}


EXPORT_FILTER_MAP = {
    "pdf": {
        FAMILY_TEXT: {"FilterName": "writer_pdf_Export"},
        FAMILY_WEB: {"FilterName": "writer_web_pdf_Export"},
        FAMILY_SPREADSHEET: {"FilterName": "calc_pdf_Export"},
        FAMILY_PRESENTATION: {"FilterName": "impress_pdf_Export"},
        FAMILY_DRAWING: {"FilterName": "draw_pdf_Export"}
    },
    "html": {
        FAMILY_TEXT: {"FilterName": "HTML (StarWriter)"},
        FAMILY_SPREADSHEET: {"FilterName": "HTML (StarCalc)"},
        FAMILY_PRESENTATION: {"FilterName": "impress_html_Export"}
    },
    "odt": {
        FAMILY_TEXT: {"FilterName": "writer8"},
        FAMILY_WEB: {"FilterName": "writerweb8_writer"}
    },
    "doc": {
        FAMILY_TEXT: {"FilterName": "MS Word 97"}
    },
    "docx": {
        FAMILY_TEXT: {"FilterName": 'MS Word 2007 XML'}
    },
    "rtf": {
        FAMILY_TEXT: {"FilterName": "Rich Text Format"}
    },
    "txt": {
        FAMILY_TEXT: {
            "FilterName": "Text",
            "FilterOptions": "utf8"
        }
    },
    "ods": {
        FAMILY_SPREADSHEET: {"FilterName": "calc8"}
    },
    "xls": {
        FAMILY_SPREADSHEET: {"FilterName": "MS Excel 97"}
    },
    "xlsx": {
        FAMILY_SPREADSHEET: {"FilterName": "Calc MS Excel 2007 XML"}
    },
    "csv": {
        FAMILY_SPREADSHEET: {
            "FilterName": "Text - txt - csv (StarCalc)",
            "FilterOptions": "44,34,0"
        }
    },
    "odp": {
        FAMILY_PRESENTATION: {"FilterName": "impress8"}
    },
    "ppt": {
        FAMILY_PRESENTATION: {"FilterName": "MS PowerPoint 97"}
    },
    "swf": {
        FAMILY_DRAWING: {"FilterName": "draw_flash_Export"},
        FAMILY_PRESENTATION: {"FilterName": "impress_flash_Export"}
    }
}

PAGE_STYLE_OVERRIDE_PROPERTIES = {
    #--- Scale options: uncomment 1 of the 3 ---
    FAMILY_SPREADSHEET: {
        # a) 'Reduce / enlarge printout': 'Scaling factor'
        "PageScale": 100,
        # b) 'Fit print range(s) to width / height': 'Width in pages' and 'Height in pages'
        #"ScaleToPagesX": 1, "ScaleToPagesY": 1000,
        # c) 'Fit print range(s) on number of pages': 'Fit print range(s) on number of pages'
        #"ScaleToPages": 1,
        "PrintGrid": False
    }
}
