
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

circ = '''
<g style="filter:url(#filter3443)">
  <circle
     r="22"
     cy="%s"
     cx="%s"
     style="opacity:1;fill:%s;fill-opacity:1;stroke:#003080;stroke-width:1px;" />
  <text
     y="%s"
     x="%s"
     style="font-size:20px;font-family:sans-serif;text-align:center;text-anchor:middle;fill:#000000;"
     xml:space="preserve">%s</text>
</g>
'''

arrow = '''
  <path 
     style="fill:none;fill-rule:evenodd;stroke:#003080;stroke-width:2px;marker-end:url(#Arrow1Lend)"
     d="m %s,%s %s,0"
     inkscape:connector-curvature="0" />
'''

end = '''
<g>
   <path d="m %s,%s 0,24"
       style="fill:none;fill-rule:evenodd;stroke:#003080;stroke-width:4px;" />
</g>
'''

err = '''
<g id="error">
    <path
       inkscape:connector-curvature="0"
       d="m %s,%s -28,36"
       style="stroke:#F00000;stroke-width:3px;" />
    <path
       style="stroke:#F00000;stroke-width:3px;"
       d="m %s,%s 28,36"
       />
</g>
'''

block = '''
<g style="filter:url(#filter3443)">
  <rect
     x="%s"
     y="%s"
     width="%s"
     height="%s"
     style="opacity:1;fill:#ffffff;fill-opacity:1;stroke:#000000;stroke-width:1px;" />
      <text
         x="%s"
         y="%s"
         style="font-size:22px;font-family:sans-serif;text-align:center;text-anchor:middle;fill:#000000;"
         xml:space="preserve">%s</text>
    </g>
'''


block_with_text = '''
<g style="filter:url(#filter3443)">
    <rect
       ry="25px"
       rx="25px"
       y="%s"
       x="%s"
       width="%s"
       height="%s"
       style="opacity:1;fill:%s;fill-opacity:1;stroke:#000000;stroke-width:1px;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1" />
</g>
'''

#==================================================
# this is the theme interface
#================================================== 
class Circle:
    def __init__(self, x, y, text, color):
        global circ
        self.node = circ % (y, x + 25, color, y + 7, x + 25, text)

class Arrow:
    def __init__(self, x, y, start, size):
        global arrow
        self.node = arrow % (x + 25 + start, y, size - 3)

class End:
    def __init__(self, x, y):
        global end
        self.node = end % (x + 25, y - 12)

class Err:
    def __init__(self, x, y):
        global err
        self.node = err % (x + 25 + 14, y - 18, x + 25 - 14, y - 18)

class BlockWithText:
    def __init__(self, x, y, text, color, width, height):
        global block_with_text
        self.node = block_with_text % (y - 22, x, width, height, "white")

class Block:
    def __init__(self, x, y, width, height, text, color):
        global block
        self.node = block % (x, y, width, height, x + width / 2.0, y + height / 2.0, text)
        
