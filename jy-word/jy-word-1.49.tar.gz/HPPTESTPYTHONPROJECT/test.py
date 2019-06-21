#! /usr/bin/env python
# coding: utf-8
__author__ = 'huo'
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')

from jy_word.File import File
from jy_word.Word import Paragraph, Set_page, Table, Tc, Tr, HyperLink, write_pkg_parts, get_imgs, get_img
img_info_path = 'img_info.json'

class Run:
    def __init__(self, img_info_path=''):
        self.test = 'hello word'
        self.familyTheme = 'minorEastAsia'
        self.family_en = 'Times New Roman'
        self.family = ''
        self.img_info_path = img_info_path

    def text(self, content, size=10.5, weight=0, underline='', space=False, wingdings=False, windChar='F09E',
             vertAlign='', lastRender=False, br='', color='', italic=False, fill='', rStyle=False, rStyleVal='', szCs=0, lang='', noProof=False):
        # https://www.jb51.net/web/560864.html
        content = str(content).replace("<", "&lt;").replace(">", "&gt;").replace('&', '&amp;')
        rFonts = '<w:rFonts w:ascii="' + self.family_en
        if self.family == '':
            rFonts += '" w:eastAsiaTheme="' + self.familyTheme
        else:
            rFonts += '" w:eastAsia="%s' % self.family
        rFonts += '" w:hAnsi="' + self.family_en + '" w:cs="Times New Roman"/>'
        sz = '<w:sz w:val="%d"/>' % int(size * 2)
        if szCs != 0:
            sz += '<w:szCs w:val="%d"/>' % int(szCs)
        uuu = ''
        weight_str = ""
        lastRendered = ''
        if weight != 0:
            weight_str = "<w:b/><w:bCs/>"
        if underline != '':
            uuu = '<w:u w:val="%s"/>' % underline
        if color != '':
            color = '<w:color w:val="%s"/>' % color
        if vertAlign == 'top':
            vertAlign = '<w:vertAlign w:val="superscript"/>'
        elif vertAlign == 'bottom':
            vertAlign = '<w:vertAlign w:val="subscript"/>'
        if italic:
            italic = '<w:i/>'
        else:
            italic = ''
        if rStyle:
            sz += '<w:rStyle w:val="%s"/>' % rStyleVal
        rPr = '<w:rPr>' + rFonts + weight_str + italic + uuu + sz + vertAlign + color
        if noProof:
            rPr += '<w:noProof/>'
        if lang != '':
            rPr += '<w:lang w:val="zh-CN"/>'
        rPr += '</w:rPr>'
        wt = ''
        if content != '':
            space1 = ''
            if space:
                space1 = ' xml:space="preserve"'
            wt = '<w:t%s>%s</w:t>' % (space1, content)
        if lastRender:
            lastRendered = '<w:lastRenderedPageBreak/>'
        wingdings1 = ''
        if wingdings:
            wingdings1 = '<w:sym w:font="Wingdings" w:char="%s"/>' % windChar
        shd = ''
        if fill != '':
            shd = '<w:shd w:val="clear" w:color="auto" w:fill="%s"/>' % fill
        r = '<w:r w:rsidRPr="008059BD">%s%s%s%s%s</w:r>' % (rPr, wingdings1, lastRendered, shd, wt)
        if br == 'column':
            r += '<w:r w:rsidR="003334DE"><w:br w:type="column"/></w:r>'
        return r

    def br(self, br_type='column'):
        r = '<w:r w:rsidR="003334DE"><w:br w:type="%s"/></w:r>' % br_type
        return r

    def picture(self, cx=0, cy=0, rId='', relativeFrom=['column', 'paragraph'], posOffset=[0, 0], align=['', ''],
                wrap='tight', text_wrapping='anchor', zoom=1):
        img_info = get_img(self.img_info_path, rId)
        if img_info is None:
            return ''
        cx1 = img_info['w']
        cy1 = img_info['h']
        if cx == 0 and cy == 0:
            zoom = zoom
        elif cx == 0 or cx * cy != 0:
            zoom = cy / cy1
        elif cy == 0:
            zoom = cx / cx1
        if cx * cy == 0:
            cx = cx1 * zoom
            cy = cy1 * zoom
        p = ['positionH', 'positionV']
        postition = ''
        srcRect = ''
        bwMode = ''
        picPr = '<pic:cNvPicPr><a:picLocks noChangeAspect="1" noChangeArrowheads="1"/></pic:cNvPicPr>'
        noFill = '<a:noFill/>'
        wp14 = ''
        framePr = '<wp:cNvGraphicFramePr>'
        framePr += '<a:graphicFrameLocks noChangeAspect="1" xmlns:a="%s/main"/>' % schemas_open_draw_2006
        framePr += '</wp:cNvGraphicFramePr>'
        if wrap == 'tight':
            wrappp = '''
            <wp:wrapTight wrapText="bothSides">
                <wp:wrapPolygon edited="0">
                    <wp:start x="4719" y="0"/>
                    <wp:lineTo x="3267" y="2919"/>
                    <wp:lineTo x="2904" y="9341"/>
                    <wp:lineTo x="0" y="14011"/>
                    <wp:lineTo x="0" y="21016"/>
                    <wp:lineTo x="1089" y="21016"/>
                    <wp:lineTo x="1452" y="21016"/>
                    <wp:lineTo x="3630" y="18681"/>
                    <wp:lineTo x="21418" y="15762"/>
                    <wp:lineTo x="21418" y="2919"/>
                    <wp:lineTo x="7261" y="0"/>
                    <wp:lineTo x="4719" y="0"/>
                </wp:wrapPolygon>
            </wp:wrapTight>'''
            framePr = '<wp:cNvGraphicFramePr/>'
            picPr = '<pic:cNvPicPr/>'
        elif wrap == 'undertext':
            wrappp = '<wp:wrapNone/>'
            srcRect = '<a:srcRect/>'
            bwMode = ' bwMode="auto"'
            noFill = ''
            wp14 = '<wp14:sizeRelH relativeFrom="page"><wp14:pctWidth>0</wp14:pctWidth></wp14:sizeRelH>'
            wp14 += '<wp14:sizeRelV relativeFrom="page"><wp14:pctHeight>0</wp14:pctHeight></wp14:sizeRelV>'
        else:
            wrappp = ''

        for i in range(0, len(p)):
            postition += '<wp:%s relativeFrom="%s">' % (p[i], relativeFrom[i])
            if align[i] != '':
                postition += '<wp:align>%s</wp:align></wp:%s>' % (align[i], p[i])
            else:
                postition += '<wp:posOffset>%d</wp:posOffset></wp:%s>' % (int(posOffset[i] * 359410), p[i])
        run = '<w:r><w:drawing><wp:%s distT="0" distB="0" ' % text_wrapping
        extent_r = 9525
        if text_wrapping == 'anchor':
            run += 'distL="114300" distR="114300" simplePos="0" relativeHeight="251658240" behindDoc="1" locked="0" layoutInCell="1" allowOverlap="1">'
            run += '<wp:simplePos x="0" y="0"/>'
            run += postition
        elif text_wrapping == 'inline':
            run += 'distL="0" distR="0">'
            wrappp = ''
            extent_r = 0
            noFill += '<a:ln w="9525"><a:noFill/><a:miter lim="800000"/><a:headEnd/><a:tailEnd/></a:ln>'
        run += '<wp:extent cx="%d" cy="%d"/>' % (int(cx * 359410), int(cy * 359410))
        run += '<wp:effectExtent l="0" t="0" r="%d" b="0"/>%s<wp:docPr id="1" name="图片 1"/>' % (extent_r, wrappp)
        run += framePr
        run += '<a:graphic xmlns:a="%s/main">' % schemas_open_draw_2006
        run += '<a:graphicData uri="%s/picture">' % schemas_open_draw_2006
        run += '<pic:pic xmlns:pic="%s/picture"><pic:nvPicPr><pic:cNvPr id="0" name=""/>' % schemas_open_draw_2006
        run += picPr

        run += '</pic:nvPicPr><pic:blipFill>'
        run += '<a:blip r:embed="rId%s"' % rId.capitalize()
        if text_wrapping != 'inline':
            run += ' cstate="print"><a:extLst><a:ext uri="{28A0092B-C50C-407E-A947-70E740481C1C}">'
            run += '<a14:useLocalDpi val="0" xmlns:a14="http://schemas.microsoft.com/office/drawing/2010/main"/>'
            run += '</a:ext></a:extLst></a:blip>'
            run += srcRect
            fill_type = '<a:stretch><a:fillRect/></a:stretch>'
        else:
            run += '/>'
            fill_type = '<a:srcRect/><a:stretch><a:fillRect/></a:stretch>'
        run += '%s</pic:blipFill>' % fill_type
        run += '<pic:spPr%s>' % bwMode
        run += '<a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm>' % (int(cx * 359410), int(cy * 359410))
        run += '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>%s</pic:spPr>' % noFill
        run += '</pic:pic></a:graphicData></a:graphic>%s' % wp14
        run += '</wp:%s></w:drawing></w:r>' % text_wrapping
        return run

    def radius(self, cx, cy, **kwargs):
        # 1cm = 72 / 2.54 pt 1in = 2.54cm = 25.4 mm = 72pt = 6pc
        cm2pt = 72 / 2.54
        cm2xml = 359410
        ''' <v:path arrowok="t" o:connecttype="custom" o:connectlocs="65089,0;325436,0;390525,65089;390525,953774;377509,966790;13016,966790;0,953774;0,65089;65089,0" o:connectangles="0,0,0,0,0,0,0,0,0"/>
               '''
        shape = 'roundrect' if 'shape' not in kwargs else kwargs['shape']
        run = '<w:r><w:pict><v:%s ' % shape
        run += 'style="position:%s;' % ('relative' if 'position' not in kwargs else kwargs['position'])
        run += 'text-align:%s;' % ('left' if 'text-align' not in kwargs else kwargs['text-align'])
        run += 'width:%.2fpt;' % (cm2pt * cx)
        run += 'height:%.2fpt;' % (cm2pt * cy)
        if 'rotation' in kwargs:
            run += 'rotation:%s;' % kwargs['rotation']
        run += 'fill'
        fangxiang = ['top', 'right', 'bottom', 'left']
        for i in range(4):
            f = fangxiang[i]
            for w in ['margin-', '', 'mso-wrap-distance-']:
                who = w + f
                run += '%s:%fpt;' % (who, 0 if who not in kwargs else kwargs[who] * cm2pt)
        run += '''z-index:251663360; visibility:visible;
                mso-wrap-style:square;
                mso-width-percent:0;
                mso-height-percent:0;
                mso-position-horizontal-relative:text;
                mso-position-vertical-relative:text;
                mso-width-percent:0;
                mso-height-percent:0;
                mso-width-relative:margin;
                mso-height-relative:margin;
                v-text-anchor:middle" '''
        if 'shape' not in kwargs:
            run += 'arcsize="19275f" '
        if 'coordsize' in kwargs:
            run += 'coordsize="%d,%d" ' % (int(cx * cm2xml), int(cy * cm2xml))
        if 'path' in kwargs:
            s = (0.05, 3)
            path = '"path=m%d,%d,' % (int(s[0] *cm2xml), int(s[1] *cm2xml))
            path += 'v%d,,' % (int(s[0]/2 * cm2xml))
            path += 'v%d,,' % (int(s[0] * cm2xml))

            run += 'path="m65089,l325436,v35948,,65089,29141,65089,65089l390525,953774v,7189,-5827,13016,-13016,13016l13016,966790c5827,966790,,960963,,953774l,65089c,29141,29141,,65089,xe" '
        run += 'fillcolor="%s" ' % '#92d050' if 'fill-color' not in kwargs else kwargs['fill-color']
        run += 'strokecolor="%s" ' % '#92d050' if 'stroke-color' not in kwargs else kwargs['stroke-color']
        run += 'strokeweight="%dpt">' % 2
        if 'para' in kwargs:
            run += '<v:textbox><w:txbxContent>%s</w:txbxContent></v:textbox>' % kwargs['para']
        run += '</v:%s></w:pict></w:r>' % shape
        return run

    def instr_text(self, text='', space=False):
        space1 = ''
        if space:
            space1 = ' xml:space="preserve"'
        if text == '1-3':
            text = 'TOC \o "1-3" \h \u '
        r1 = '<w:r><w:instrText%s>%s</w:instrText></w:r>' % (space1, text)
        return r1

    def fldChar(self, fldCharType='separate'):
        r1 = '<w:r><w:fldChar w:fldCharType="%s"/></w:r>' % fldCharType
        return r1

    def tab(self):
        r1 = '<w:r><w:rPr><w:rFonts w:eastAsiaTheme="%s"/></w:rPr><w:tab/></w:r>' % self.familyTheme
        return r1

    def style(self, text, val='af8'):
        r = '<w:r><w:rPr><w:rStyle w:val="%s"/><w:rFonts w:eastAsiaTheme="%s"/></w:rPr><w:t>%s</w:t></w:r>' % (val, self.familyTheme, text)
        return r

my_file = File()

r = Run(img_info_path)
hyperlink = HyperLink()
r.family_en = 'Times New Roman'
p = Paragraph()
set_page = Set_page().set_page
table = Table()
tr = Tr()
tc = Tc()

# 初号=42磅
# 小初=36磅
# 一号=26磅
# 小一=24磅
# 二号=22磅
# 小二=18磅
# 三号=16磅
# 小三=15磅
# 四号=14磅
# 小四=12磅
# 五号=10.5磅
# 小五=9磅
# 六号=7.5磅
# 小六=6.5磅
# 七号=5.5磅
# 八号=5磅


# ##################下载报告所需方法######################

def generate_word():
    file_name = 'my_word.doc'
    print u'%s begin.' % file_name
    imgs = get_imgs(os.path.dirname(__file__))
    my_file.write(img_info_path, imgs)
    body = p.h4('hello, my word!', size=28, spacing=[3, 3])
    body += p.write(r.radius(1, 3, para=p.write(r.text('rotation')), rotation='-90', shape='shape', path='df', coordsize=(0.5, 0.5)))
    tcs = tc.write(tc.set(2000), p.write(r.radius(3, 1, para=p.write(r.text('testdd')))))

    trs = tr.write(tcs, tr.set(trHeight=680))
    body += table.write(trs, [2000])
    # body += p.write(r.picture(cx=10, rId='ex'))
    pkg = write_pkg_parts(imgs, body, title=[])
    my_file.download(pkg, file_name)
    print u'%s over.' % file_name



if __name__ == '__main__':
    generate_word()
