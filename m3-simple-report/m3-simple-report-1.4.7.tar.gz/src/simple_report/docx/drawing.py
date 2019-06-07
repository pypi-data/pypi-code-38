# coding: utf-8
from __future__ import absolute_import

import os
import shutil
import uuid

from lxml import etree


DRAWING_XML = """<w:drawing xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
    xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
    xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"
    xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
    <wp:inline>
    <wp:extent cx="%(width)s" cy="%(height)s"/>
    <wp:docPr id="%(docPr_id)s" name="%(picture_name)s"/>
    <a:graphic>
        <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
            <pic:pic>
                <pic:nvPicPr>
                    <pic:cNvPr id="0" name="%(filename)s"/>
                    <pic:cNvPicPr/>
                </pic:nvPicPr>
                <pic:blipFill>
                    <a:blip r:embed="%(rId_name)s"/>
                    <a:stretch>
                        <a:fillRect/>
                    </a:stretch>
                </pic:blipFill>
                <pic:spPr>
                    <a:xfrm>
                        <a:off x="0" y="0"/>
                        <a:ext cx="9753600" cy="7315200"/>
                    </a:xfrm>
                    <a:prstGeom prst="rect"/>
                </pic:spPr>
            </pic:pic>
        </a:graphicData>
    </a:graphic>
    </wp:inline>
</w:drawing>"""


class DocxImage(object):
    """
    Рисунок для вставки в документ DOCX
    """
    def __init__(self, filepath, width, height):
        self.filepath = filepath
        self.width = width
        self.height = height


def insert_image(text_node, docx_image, text_to_replace, doc_rels):
    """
    Вставляет рисунок в документ DOCX
    """

    emu_in_inch = 914000
    sm_in_inch = 2.54

    r_node = text_node.getparent()
    image_filename = os.path.basename(docx_image.filepath)

    text_node.text = text_node.text.replace(text_to_replace, '')
    parser = etree.XMLParser(ns_clean=True)
    rid = doc_rels.next_rid()
    drawing_node = etree.fromstring(
        DRAWING_XML % {
            'filename': image_filename,
            'picture_name': 'Picture 100',
            'rId_name': rid,
            'docPr_id': uuid.uuid4(),
            'width': int(emu_in_inch * float(docx_image.width) // sm_in_inch),
            'height': int(emu_in_inch * float(docx_image.height) // sm_in_inch)
        },
        # parser=parser
    )
    media_folder = os.path.join(doc_rels.current_folder, 'word', 'media')
    if not os.path.exists(media_folder):
        os.makedirs(media_folder)
    shutil.copy(
        docx_image.filepath,
        os.path.join(
            media_folder,
            image_filename
        )
    )
# <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image1.jpeg"/>
    etree.SubElement(doc_rels._root, 'Relationship', attrib={
        'Id': rid,
        'Type': "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
        'Target': 'media/%s' % image_filename
    })

    r_node.append(drawing_node)
