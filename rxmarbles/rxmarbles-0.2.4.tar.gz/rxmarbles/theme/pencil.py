from numpy.random import random
import random

root = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   width="%spx"
   height="%spx"
   viewBox="0 0 %s %s "
   id="svg2"
   version="1.1"
   inkscape:version="0.91 r13725"
  >
  <defs
     id="defs4"> 
<filter
       style="color-interpolation-filters:sRGB;"
       inkscape:label="Drop Shadow"
       id="filter3443"
        x="-25%%"
        y="-25%%"
        width="150%%"        
        height="150%%"        
        >
      <feFlood
         flood-opacity="0.498039"
         flood-color="rgb(0,0,0)"
         result="flood"
         id="feFlood3445" />
      <feComposite
         in="flood"
         in2="SourceGraphic"
         operator="in"
         result="composite1"
         id="feComposite3447" />
      <feGaussianBlur
         in="composite1"
         stdDeviation="3"
         result="blur"
         id="feGaussianBlur3449" />
      <feOffset
         dx="2"
         dy="3"
         result="offset"
         id="feOffset3451" />
      <feComposite
         in="SourceGraphic"
         in2="offset"
         operator="over"
         result="composite2"
         id="feComposite3453" />
    </filter>
    <marker
       inkscape:stockid="Arrow1Lend"
       orient="auto"
       refY="0.0"
       refX="0.0"
       id="Arrow1Lend"
       style="overflow:visible;"
       inkscape:isstock="true">
      <path
         d="M -3.0,0.0 L -3.0,-5.0 L -12.5,0.0 L -3.0,5.0 L -3.0,0.0 z "
         style="fill-rule:evenodd;stroke:#003080;stroke-width:1pt;stroke-opacity:1;fill:#003080;fill-opacity:1"
         transform="scale(0.8) rotate(180) translate(12.5,0)" />
    </marker>    

  </defs>
    %s
 </svg>
'''

circ1 = '''
<g transform="translate(%s %s)">
<path
     sodipodi:nodetypes="cccc"
     inkscape:connector-curvature="0"
     id="circle"
     d="m 4.9388474,-19.439462 c 16.0642996,-0.12398 28.5596096,25.2132203 13.6726596,35.64262 -11.0573896,9.63907 -34.34364,12.39205 -40.14488,-4.43275 -5.99947,-18.2070397 12.2740204,-28.34201 25.6703704,-34.96158"
     style="fill:#ffffff;fill-opacity:0.8627451;fill-rule:evenodd;stroke:#000000;stroke-width:1.42857146px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"
     inkscape:label="#path3567" />
     
  <text
     y="11"
     x="0"
     style="font-size:28px;font-family:purisa;text-align:center;text-anchor:middle;fill:#000000;"
     xml:space="preserve">%s</text>
</g>
'''
circ2 = '''
    <g transform="translate(%s %s)">
    <path
     sodipodi:nodetypes="ccc"
     style="fill:#ffffff;fill-opacity:0.8627451;fill-rule:evenodd;stroke:#000000;stroke-width:1.42857158px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"
     d="M 1.5925919,21.477458 C 54.657578,22.391841 -4.4465257,-49.196211 -20.218549,-5.7426508 -25.112801,8.7120558 -15.351552,21.857363 2.9582607,24.135679"
     id="circ2"
     inkscape:connector-curvature="0"
     inkscape:label="#path3569" />
  <text
     y="11"
     x="0"
     style="font-size:28px;font-family:purisa;text-align:center;text-anchor:middle;fill:#000000;"
     xml:space="preserve">%s</text>
</g>
'''
circ3 = '''
<g transform="translate(%s %s)">
    <path
     sodipodi:nodetypes="ccccc"
     inkscape:connector-curvature="0"
     id="circ3"
     d="M 4.0475415,-21.306002 C -11.703304,-26.547792 -23.641751,-7.9231854 -22.516473,6.1088129 -20.059942,26.830243 12.722358,33.867273 22.337406,14.863588 27.656584,4.0579388 23.204578,-8.3517124 15.784624,-16.859919 c -1.822,-3.127279 -5.336267,-5.723574 -9.3972065,-5.54123"
     style="fill:#ffffff;fill-opacity:0.8627451;fill-rule:evenodd;stroke:#000000;stroke-width:1.42857158px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"
     inkscape:label="#path3571" />
  <text
     y="11"
     x="0"
     style="font-size:28px;font-family:purisa;text-align:center;text-anchor:middle;fill:#000000;"
     xml:space="preserve">%s</text>
</g>
'''
circ4 = '''
<g transform="translate(%s %s)">
    <path
     style="fill:#ffffff;fill-opacity:0.8627451;fill-rule:evenodd;stroke:#000000;stroke-width:1.42857146px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"
     d="M 2.0536007,-17.942742 C -52.370629,-18.905944 8.2474086,56.504162 24.423439,10.730643 29.443049,-4.4957928 16.207176,-22.177911 -2.5716488,-24.577866"
     id="circ5"
     inkscape:connector-curvature="0"
     inkscape:label="#path3433" />
  <text
     y="11"
     x="0"
     style="font-size:28px;font-family:purisa;text-align:center;text-anchor:middle;fill:#000000;"
     xml:space="preserve">%s</text>
</g>
'''
arrow = '''
<g transform="scale(%s %s) translate(%s %s)">
  <path
     style="fill:none;fill-rule:evenodd;stroke:#000000;stroke-width:2px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"
     d="M -0.67660398,1.4566587 C 51.393331,1.3820987 103.49025,-3.9934243 155.52767,1.1808467 c 33.34887,0.89417 67.21197,-1.95060293 99.84156,5.535708 44.03188,2.2890288 88.09651,1.698567 131.74849,-3.79605 21.2474,-0.841106 42.51228,0.139269 63.76647,-0.199798"
     id="axisLine"
     inkscape:connector-curvature="0"
     inkscape:label="#path3511" />
</g>
<g transform="translate(%s %s)">
  <path
     style="fill:none;fill-rule:evenodd;stroke:#000000;stroke-width:1.42857146px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"
     d="m -13.085216,-10.419073 c 2.66757,0.133318 4.1293297,2.8477214 6.5645197,3.6415244 2.19618,1.483387 4.27915,3.129365 6.74184,4.165938 3.6572898,1.62997797 0.28555,4.903303 -1.90365,6.045673 -2.08841,1.84505 -3.80877,3.732465 -6.63704,4.785017 -1.8518597,0.870578 -3.6440197,1.8066886 -5.3976897,2.8506076"
     id="arrow_end"
     inkscape:connector-curvature="0"
     inkscape:label="#path3528" />
</g>

'''

end = '''
<g>
   <path d="m %s,%s -1,32"
       style="fill:none;fill-rule:evenodd;stroke:#000000;stroke-width:4px;" />
</g>
'''

err = '''
<g id="error">
    <path
       inkscape:connector-curvature="0"
       d="m %s,%s -34,36"
       style="stroke:#000000;stroke-width:3px;" />
    <path
       style="stroke:#000000;stroke-width:3px;"
       d="m %s,%s 36,36"
       />
</g>
'''
# this one is used for operator box
block = '''
<g transform="scale(%s %s) translate(%s %s)">
<path
     style="fill:#ffffff;fill-rule:evenodd;stroke:#000000;stroke-width:1.42857146px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"
     d="M 3.6131775,2.4809559 C 7.7262916,27.136376 -4.8390181,67.388756 10.311791,81.793736 c 56.57601,-7.35809 113.842299,-2.82956 170.815959,-4.56434 48.9116,1.31804 98.12281,2.30369 146.89949,0.25237 36.73272,-6.08907 74.34343,-4.60865 110.81369,1.7655 26.17801,-6.87142 7.26874,-47.02276 10.85636,-67.94864 C 435.2653,-11.614984 389.13054,8.5049456 362.01772,0.90526594 300.94038,0.67314594 239.26649,2.7131859 178.67384,0.60705594 118.08119,-1.4990741 86.699905,6.8117156 57.753682,4.3549359 28.807462,1.8981559 17.816805,1.4648659 0.01403178,-4.669534"
     id="operator_box"
     inkscape:connector-curvature="0"
     sodipodi:nodetypes="ccccccczzc"
     inkscape:label="#path3549" />
</g>
      <text
         x="%s"
         y="%s"
         style="font-size:24px;font-family:purisa;text-align:center;text-anchor:middle;fill:#000000;"
         xml:space="preserve">%s</text>

'''

# - this one is used for groupping
groupping_block = '''
<g >
    <rect
       ry="25px"
       rx="25px"
       y="%s"
       x="%s"
       width="%s"
       height="%s"
       style="opacity:1;fill:%s;fill-opacity:0;stroke:#000000;stroke-width:1px;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1" />
</g>
'''

#==================================================
# this is the theme interface
#================================================== 
class Circle:
    def __init__(self, x, y, text, color):
        global circ1
        global circ2
        global circ3
        shapes = [circ1, circ2, circ3]
        index = random.randint(0, len(shapes) - 1)
        circ = shapes[index]
        self.node = circ % (x + 25, y, text)

class Arrow:
    def __init__(self, x, y, start, size):
        global arrow
        self.node = arrow % (1.0 * size / 450.0, 0.75, x + 25 + start, y, x + 22 + start + size, y + 2)

class End:
    def __init__(self, x, y):
        global end
        self.node = end % (x + 25, y - 12)

class Err:
    def __init__(self, x, y):
        global err
        self.node = err % (x + 25 + 18, y - 18, x + 25 - 14, y - 18)

class BlockWithText:
    def __init__(self, x, y, text, color, width, height):
        global groupping_block
        self.node = groupping_block % (y - 22, x, width, height, "white")

class Block:
    def __init__(self, x, y, width, height, text, color):
        global block
        self.node = block % (width / 460.0, 1, x, y, x + width / 2.0, y + height / 2.0, text)
