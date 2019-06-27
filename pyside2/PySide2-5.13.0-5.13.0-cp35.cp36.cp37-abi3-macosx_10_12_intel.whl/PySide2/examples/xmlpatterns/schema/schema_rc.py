# -*- coding: utf-8 -*-

# Resource object code
#
# Created: Wed Jun 26 06:52:17 2019
#      by: The Resource Compiler for PySide2 (Qt v5.13.0)
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore

qt_resource_data = b"\
\x00\x00\x06\x05\
<\
?xml version=\x221.\
0\x22?>\x0a<xsd:schema\
 xmlns:xsd=\x22http\
://www.w3.org/20\
01/XMLSchema\x22>\x0a\x0a\
    <xsd:element\
 name=\x22recipe\x22>\x0a\
        <xsd:com\
plexType>\x0a      \
      <xsd:seque\
nce>\x0a           \
     <xsd:elemen\
t name=\x22title\x22 t\
ype=\x22xsd:string\x22\
/>\x0a             \
   <xsd:element \
name=\x22ingredient\
\x22 type=\x22ingredie\
ntType\x22 maxOccur\
s=\x22unbounded\x22/>\x0a\
                \
<xsd:element nam\
e=\x22time\x22 type=\x22t\
imeType\x22/>\x0a     \
           <xsd:\
element name=\x22me\
thod\x22>\x0a         \
           <xsd:\
complexType>\x0a   \
                \
     <xsd:sequen\
ce>\x0a            \
                \
<xsd:element nam\
e=\x22step\x22 type=\x22x\
sd:string\x22 maxOc\
curs=\x22unbounded\x22\
/>\x0a             \
           </xsd\
:sequence>\x0a     \
               <\
/xsd:complexType\
>\x0a              \
  </xsd:element>\
\x0a            </x\
sd:sequence>\x0a   \
     </xsd:compl\
exType>\x0a    </xs\
d:element>\x0a\x0a    \
<xsd:complexType\
 name=\x22ingredien\
tType\x22>\x0a        \
<xsd:attribute n\
ame=\x22name\x22 type=\
\x22xsd:string\x22/>\x0a \
       <xsd:attr\
ibute name=\x22quan\
tity\x22 type=\x22xsd:\
positiveInteger\x22\
/>\x0a        <xsd:\
attribute name=\x22\
unit\x22 type=\x22xsd:\
string\x22/>\x0a    </\
xsd:complexType>\
\x0a\x0a    <xsd:compl\
exType name=\x22tim\
eType\x22>\x0a        \
<xsd:attribute n\
ame=\x22quantity\x22 t\
ype=\x22xsd:positiv\
eInteger\x22/>\x0a    \
    <xsd:attribu\
te name=\x22unit\x22>\x0a\
            <xsd\
:simpleType>\x0a   \
             <xs\
d:restriction ba\
se=\x22xsd:string\x22>\
\x0a               \
     <xsd:enumer\
ation value=\x22sec\
onds\x22/>\x0a        \
            <xsd\
:enumeration val\
ue=\x22minutes\x22/>\x0a \
                \
   <xsd:enumerat\
ion value=\x22hours\
\x22/>\x0a            \
    </xsd:restri\
ction>\x0a         \
   </xsd:simpleT\
ype>\x0a        </x\
sd:attribute>\x0a  \
  </xsd:complexT\
ype>\x0a\x0a</xsd:sche\
ma>\x0a\
\x00\x00\x01*\
<\
contact>\x0a    <gi\
venName>John</gi\
venName>\x0a    <fa\
milyName>Doe</fa\
milyName>\x0a    <b\
irthdate>1977-12\
-25</birthdate>\x0a\
    <homeAddress\
>\x0a        <stree\
t>Sandakerveien \
116</street>\x0a   \
     <zipCode>N-\
0550</zipCode>\x0a \
       <city>Osl\
o</city>\x0a       \
 <country>Norway\
</country>\x0a    <\
/homeAddress>\x0a</\
contact>\x0a\
\x00\x00\x01\xb6\
<\
order>\x0a    <cust\
omerId>194223</c\
ustomerId>\x0a    <\
article>\x0a       \
 <articleId>2224\
2</articleId>\x0a  \
      <count>5</\
count>\x0a    </art\
icle>\x0a    <artic\
le>\x0a        <art\
icleId>32372</ar\
ticleId>\x0a       \
 <count>12</coun\
t>\x0a        <comm\
ent>without stri\
pes</comment>\x0a  \
  </article>\x0a   \
 <article>\x0a     \
   <articleId>23\
649</articleId>\x0a\
        <count>2\
</count>\x0a    </a\
rticle>\x0a    <del\
iveryDate>2009-0\
1-23</deliveryDa\
te>\x0a    <payed>t\
rue</payed>\x0a</or\
der>\x0a\
\x00\x00\x03\xbb\
<\
?xml version=\x221.\
0\x22?>\x0a<xsd:schema\
 xmlns:xsd=\x22http\
://www.w3.org/20\
01/XMLSchema\x22>\x0a\x0a\
    <xsd:element\
 name=\x22contact\x22>\
\x0a        <xsd:co\
mplexType>\x0a     \
       <xsd:sequ\
ence>\x0a          \
      <xsd:eleme\
nt name=\x22givenNa\
me\x22 type=\x22xsd:st\
ring\x22/>\x0a        \
        <xsd:ele\
ment name=\x22famil\
yName\x22 type=\x22xsd\
:string\x22/>\x0a     \
           <xsd:\
element name=\x22bi\
rthdate\x22 type=\x22x\
sd:date\x22 minOccu\
rs=\x220\x22/>\x0a       \
         <xsd:el\
ement name=\x22home\
Address\x22 type=\x22a\
ddress\x22/>\x0a      \
          <xsd:e\
lement name=\x22wor\
kAddress\x22 type=\x22\
address\x22 minOccu\
rs=\x220\x22/>\x0a       \
     </xsd:seque\
nce>\x0a        </x\
sd:complexType>\x0a\
    </xsd:elemen\
t>\x0a\x0a    <xsd:com\
plexType name=\x22a\
ddress\x22>\x0a       \
 <xsd:sequence>\x0a\
            <xsd\
:element name=\x22s\
treet\x22 type=\x22xsd\
:string\x22/>\x0a     \
       <xsd:elem\
ent name=\x22zipCod\
e\x22 type=\x22xsd:str\
ing\x22/>\x0a         \
   <xsd:element \
name=\x22city\x22 type\
=\x22xsd:string\x22/>\x0a\
            <xsd\
:element name=\x22c\
ountry\x22 type=\x22xs\
d:string\x22/>\x0a    \
    </xsd:sequen\
ce>\x0a    </xsd:co\
mplexType>\x0a\x0a</xs\
d:schema>\x0a\
\x00\x00\x02U\
<\
recipe>\x0a    <tit\
le>Cheese on Toa\
st</title>\x0a    <\
ingredient name=\
\x22Bread\x22 quantity\
=\x222\x22 unit=\x22slice\
s\x22/>\x0a    <ingred\
ient name=\x22Chees\
e\x22 quantity=\x222\x22 \
unit=\x22slices\x22/>\x0a\
    <time quanti\
ty=\x223\x22 unit=\x22day\
s\x22/>\x0a    <method\
>\x0a        <step>\
1. Slice the bre\
ad and cheese.</\
step>\x0a        <s\
tep>2. Grill one\
 side of each sl\
ice of bread.</s\
tep>\x0a        <st\
ep>3. Turn over \
the bread and pl\
ace a slice of c\
heese on each pi\
ece.</step>\x0a    \
    <step>4. Gri\
ll until the che\
ese has started \
to melt.</step>\x0a\
        <step>5.\
 Serve and enjoy\
!</step>\x0a    </m\
ethod>\x0a    <comm\
ent>Tell your fr\
iends about it!<\
/comment>\x0a</reci\
pe>\x0a\
\x00\x00\x02%\
<\
recipe>\x0a    <tit\
le>Cheese on Toa\
st</title>\x0a    <\
ingredient name=\
\x22Bread\x22 quantity\
=\x222\x22 unit=\x22slice\
s\x22/>\x0a    <ingred\
ient name=\x22Chees\
e\x22 quantity=\x222\x22 \
unit=\x22slices\x22/>\x0a\
    <time quanti\
ty=\x223\x22 unit=\x22min\
utes\x22/>\x0a    <met\
hod>\x0a        <st\
ep>1. Slice the \
bread and cheese\
.</step>\x0a       \
 <step>2. Grill \
one side of each\
 slice of bread.\
</step>\x0a        \
<step>3. Turn ov\
er the bread and\
 place a slice o\
f cheese on each\
 piece.</step>\x0a \
       <step>4. \
Grill until the \
cheese has start\
ed to melt.</ste\
p>\x0a        <step\
>5. Serve and en\
joy!</step>\x0a    \
</method>\x0a</reci\
pe>\x0a\
\x00\x00\x03g\
<\
?xml version=\x221.\
0\x22?>\x0a<xsd:schema\
 xmlns:xsd=\x22http\
://www.w3.org/20\
01/XMLSchema\x22>\x0a\x0a\
    <xsd:element\
 name=\x22order\x22>\x0a \
       <xsd:comp\
lexType>\x0a       \
     <xsd:sequen\
ce>\x0a            \
    <xsd:element\
 name=\x22customerI\
d\x22 type=\x22xsd:pos\
itiveInteger\x22/>\x0a\
                \
<xsd:element nam\
e=\x22article\x22 type\
=\x22articleType\x22 m\
axOccurs=\x22unboun\
ded\x22/>\x0a         \
       <xsd:elem\
ent name=\x22delive\
ryDate\x22 type=\x22xs\
d:date\x22/>\x0a      \
          <xsd:e\
lement name=\x22pay\
ed\x22 type=\x22xsd:bo\
olean\x22/>\x0a       \
     </xsd:seque\
nce>\x0a        </x\
sd:complexType>\x0a\
    </xsd:elemen\
t>\x0a\x0a    <xsd:com\
plexType name=\x22a\
rticleType\x22>\x0a   \
     <xsd:sequen\
ce>\x0a            \
<xsd:element nam\
e=\x22articleId\x22 ty\
pe=\x22xsd:positive\
Integer\x22/>\x0a     \
       <xsd:elem\
ent name=\x22count\x22\
 type=\x22xsd:posit\
iveInteger\x22/>\x0a  \
          <xsd:e\
lement name=\x22com\
ment\x22 type=\x22xsd:\
string\x22 minOccur\
s=\x220\x22/>\x0a        \
</xsd:sequence>\x0a\
    </xsd:comple\
xType>\x0a\x0a</xsd:sc\
hema>\x0a\
\x00\x00\x01\x1d\
<\
contact>\x0a    <gi\
venName>John</gi\
venName>\x0a    <fa\
milyName>Doe</fa\
milyName>\x0a    <t\
itle>Prof.</titl\
e>\x0a    <workAddr\
ess>\x0a        <st\
reet>Sandakervei\
en 116</street>\x0a\
        <zipCode\
>N-0550</zipCode\
>\x0a        <city>\
Oslo</city>\x0a    \
    <country>Nor\
way</country>\x0a  \
  </workAddress>\
\x0a</contact>\x0a\
\x00\x00\x01.\
<\
order>\x0a    <cust\
omerId>234219</c\
ustomerId>\x0a    <\
article>\x0a       \
 <articleId>2169\
2</articleId>\x0a  \
      <count>3</\
count>\x0a    </art\
icle>\x0a    <artic\
le>\x0a        <art\
icleId>24749</ar\
ticleId>\x0a       \
 <count>9</count\
>\x0a    </article>\
\x0a    <deliveryDa\
te>2009-01-23</d\
eliveryDate>\x0a   \
 <payed>yes</pay\
ed>\x0a</order>\x0a\
"

qt_resource_name = b"\
\x00\x0c\
\x08\x13\x87\xf4\
\x00s\
\x00c\x00h\x00e\x00m\x00a\x00_\x001\x00.\x00x\x00s\x00d\
\x00\x0e\
\x00vJ\x1c\
\x00i\
\x00n\x00s\x00t\x00a\x00n\x00c\x00e\x00_\x000\x00.\x00x\x00m\x00l\
\x00\x0e\
\x00rJ\x1c\
\x00i\
\x00n\x00s\x00t\x00a\x00n\x00c\x00e\x00_\x004\x00.\x00x\x00m\x00l\
\x00\x0c\
\x08\x10\x87\xf4\
\x00s\
\x00c\x00h\x00e\x00m\x00a\x00_\x000\x00.\x00x\x00s\x00d\
\x00\x0e\
\x00sJ\x1c\
\x00i\
\x00n\x00s\x00t\x00a\x00n\x00c\x00e\x00_\x003\x00.\x00x\x00m\x00l\
\x00\x0e\
\x00pJ\x1c\
\x00i\
\x00n\x00s\x00t\x00a\x00n\x00c\x00e\x00_\x002\x00.\x00x\x00m\x00l\
\x00\x0c\
\x08\x16\x87\xf4\
\x00s\
\x00c\x00h\x00e\x00m\x00a\x00_\x002\x00.\x00x\x00s\x00d\
\x00\x0e\
\x00yJ\x1c\
\x00i\
\x00n\x00s\x00t\x00a\x00n\x00c\x00e\x00_\x001\x00.\x00x\x00m\x00l\
\x00\x0e\
\x00uJ\x1c\
\x00i\
\x00n\x00s\x00t\x00a\x00n\x00c\x00e\x00_\x005\x00.\x00x\x00m\x00l\
"

qt_resource_struct = b"\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x09\x00\x00\x00\x01\
\x00\x00\x00\xa2\x00\x00\x00\x00\x00\x01\x00\x00\x0f\x09\
\x00\x00\x00@\x00\x00\x00\x00\x00\x01\x00\x00\x077\
\x00\x00\x00\x80\x00\x00\x00\x00\x00\x01\x00\x00\x0c\xb0\
\x00\x00\x01\x04\x00\x00\x00\x00\x00\x01\x00\x00\x15\xbe\
\x00\x00\x00\x1e\x00\x00\x00\x00\x00\x01\x00\x00\x06\x09\
\x00\x00\x00\xe2\x00\x00\x00\x00\x00\x01\x00\x00\x14\x9d\
\x00\x00\x00b\x00\x00\x00\x00\x00\x01\x00\x00\x08\xf1\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\
\x00\x00\x00\xc4\x00\x00\x00\x00\x00\x01\x00\x00\x112\
"

def qInitResources():
    QtCore.qRegisterResourceData(0x01, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(0x01, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()
