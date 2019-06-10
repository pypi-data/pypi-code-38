

import math

from decimal import Decimal

from .. import tag

from . import Widget, ClosedWidget, FieldArg, FieldArgList, FieldArgTable, FieldArgDict


class Arrow1(ClosedWidget):
    """An svg arrow shape, fitting in a 100x100 space
    """

    # This class does not display any error messages
    display_errors = False

    _points = ((49,1), (50,1), (98,30), (98,32), (60,32), (60,98), (39,98), (39,32), (1,32), (1,30))

    arg_descriptions = {'fill':FieldArg("text", "none", jsonset=True),
                        'stroke':FieldArg("text", "black", jsonset=True),
                        'transform':FieldArg("text", "", jsonset=True),
                        'stroke_width':FieldArg("text", "1", jsonset=True)
                       }

    def __init__(self, name=None, brief='', **field_args):
        """
        fill: The fill colour, use none for no fill
        stroke: The outline edge colour
        stroke_width: The outline edge thickness
        transform: The svg transform object, use it to scals and rotate
        """
        ClosedWidget.__init__(self, name=name, tag_name="polygon", brief=brief, **field_args)

    def _build(self, page, ident_list, environ, call_data, lang):
        "create arrow"                  
        attrib_points = ""
        for p in self._points:
            point = "%s, %s " % p
            attrib_points += point
        self.update_attribs({"points":attrib_points})

        if self.get_field_value("fill"):
            self.update_attribs({"fill":self.get_field_value("fill")})
        if self.get_field_value("stroke"):
            self.update_attribs({"stroke":self.get_field_value("stroke")})
        if self.get_field_value("transform"):
            self.update_attribs({"transform":self.get_field_value("transform")})
        if self.get_field_value("stroke_width"):
            self.update_attribs({"stroke-width":self.get_field_value("stroke_width")})

    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<polygon /> <!-- arrow shape with widget id, class widget_class and the given attributes -->"""



class Arrow2(ClosedWidget):
    """A slim svg arrow shape, fitting in a 50x200 space
    """

    # This class does not display any error messages
    display_errors = False

    _points = ((24,1), (25,1), (49,50), (49,52), (30,52), (30,198), (19,198), (19,52), (1,52), (1,50))

    arg_descriptions = {'fill':FieldArg("text", "none", jsonset=True),
                        'stroke':FieldArg("text", "black", jsonset=True),
                        'transform':FieldArg("text", "", jsonset=True),
                        'stroke_width':FieldArg("text", "1", jsonset=True)
                       }

    def __init__(self, name=None, brief='', **field_args):
        """
        fill: The fill colour, use none for no fill
        stroke: The outline edge colour
        stroke_width: The outline edge thickness
        transform: The svg transform object, use it to scals and rotate
        """
        ClosedWidget.__init__(self, name=name, tag_name="polygon", brief=brief, **field_args)

    def _build(self, page, ident_list, environ, call_data, lang):
        "create arrow"                  
        attrib_points = ""
        for p in self._points:
            point = "%s, %s " % p
            attrib_points += point
        self.update_attribs({"points":attrib_points})

        if self.get_field_value("fill"):
            self.update_attribs({"fill":self.get_field_value("fill")})
        if self.get_field_value("stroke"):
            self.update_attribs({"stroke":self.get_field_value("stroke")})
        if self.get_field_value("transform"):
            self.update_attribs({"transform":self.get_field_value("transform")})
        if self.get_field_value("stroke_width"):
            self.update_attribs({"stroke-width":self.get_field_value("stroke_width")})

    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<polygon /> <!-- arrow shape with widget id, class widget_class and the given attributes -->"""


class Vertical1(Widget):

    # This class does not display any error messages
    display_errors = False

    _points = ((110,49), (110,50), (81,98), (79,98), (79,60), (13,60), (13,39), (79,39), (79,1), (81,1))

    arg_descriptions = {
                        'transform':FieldArg("text", "", jsonset=True),
                        'arrow_fill':FieldArg("text", "blue", jsonset=True),
                        'minimum':FieldArg("text", "0"),
                        'maximum':FieldArg("text", "100"),
                        'smallintervals':FieldArg("text", "10"),
                        'largeintervals':FieldArg("text", "20"),
                        'measurement':FieldArg("text", "50", jsonset=True),
                        'font_family':FieldArg("text", "arial")
                       }


    def _make_scale(self, minimum, maximum, smallintervals, largeintervals):
        "Returns two lists of Decimal values"

        minvalue = Decimal(minimum)
        maxvalue = Decimal(maximum)
        smallint = Decimal(smallintervals)
        largeint = Decimal(largeintervals)
       
        # start at the bottom of the scale with minvalue
        minscale = [minvalue]
        maxscale = [minvalue]
        mns = minvalue
        mxs = minvalue

        while mxs < maxvalue:
            mxs += largeint
            maxscale.append(mxs)

        while True:
            mns += smallint
            if mns > maxscale[-1]:
                break
            minscale.append(mns)
        return minscale, maxscale

    def __init__(self, name=None, brief='', **field_args):
        """A g element which holds a vertical scale and arrow, held in a 700 high x 250 wide space"""
        Widget.__init__(self, name=name, tag_name="g", brief=brief, **field_args)
        self[0] = tag.ClosedPart(tag_name='rect', attribs={"x":"100",
                                                           "y":"1",
                                                           "rx":"2",
                                                           "ry":"2",
                                                           "width":"149",
                                                           "height":"698",
                                                           "fill":"white",
                                                           "stroke":"black",
                                                           "stroke-width":"1"})
        arrow_points = ""
        for p in self._points:
            point = "%s, %s " % p
            arrow_points += point
        self[1] = tag.ClosedPart(tag_name='polygon', attribs={
                                                           "fill":"white",
                                                           "stroke":"black",
                                                           "stroke-width":"2",
                                                           "points":arrow_points })
        self[2] = tag.ClosedPart(tag_name='line', attribs={
                                                            'x1':'120',
                                                            'y1':'50',
                                                            'x2':'120',
                                                            'y2':'650',
                                                            'stroke':"black",
                                                            'stroke-width':"2"  })


    def _build(self, page, ident_list, environ, call_data, lang):
        if self.get_field_value("transform"):
            self.update_attribs({"transform":self.get_field_value("transform")})

        font_family = self.get_field_value("font_family")
        if not font_family:
            font_family = "arial"

        if self.get_field_value("arrow_fill"):
            self[1].update_attribs({"fill":self.get_field_value("arrow_fill")})
        # make the scale
        minscale, maxscale = self._make_scale(self.get_field_value("minimum"),
                                              self.get_field_value("maximum"),
                                              self.get_field_value("smallintervals"),
                                              self.get_field_value("largeintervals"))

        # small lines
        minitems = len(minscale)
        scalemins = Decimal('600.0') / (minitems-1)
        n = 3
        for index, item in enumerate(minscale):
            vert = Decimal(650) - index*scalemins
            self[n] = tag.ClosedPart(tag_name='line', attribs={
                                                            'x1':'120',
                                                            'y1': str(vert),
                                                            'x2':'150',
                                                            'y2':str(vert),
                                                            'stroke':"black",
                                                            'stroke-width':"1"  })
            n += 1

        # large lines
        maxitems = len(maxscale)
        scalemaxs = Decimal('600.0') / (maxitems-1)
        for index, item in enumerate(maxscale):
            vert = Decimal('650') - index*scalemaxs
            self[n] = tag.ClosedPart(tag_name='line', attribs={
                                                            'x1':'119',
                                                            'y1': str(vert),
                                                            'x2':'210',
                                                            'y2':str(vert),
                                                            'stroke':"black",
                                                            'stroke-width':"3"  })

            n += 1
            self[n] = tag.Part(tag_name='text', text=str(item), attribs={
                                                            'x':'160',
                                                            'y': str(vert-10),
                                                            'font-size': '20',
                                                            'font-family': font_family,
                                                            'stroke':"black",
                                                            'stroke-width':"1"  })

            n += 1

        # now place arrow at the measurement point
        measurement = Decimal(self.get_field_value("measurement"))
        self._minvalue = maxscale[0]
        self._maxvalue = maxscale[-1]
        if measurement >= self._maxvalue:
            return
        if measurement <= self._minvalue:
            self[1].update_attribs({"transform" : "translate(0, 600)"})
            return
        m = Decimal('600.0') - (measurement - self._minvalue)*600/(self._maxvalue-self._minvalue)
        self[1].update_attribs({"transform" : "translate(0, %s)" % (m,)})

    def _build_js(self, page, ident_list, environ, call_data, lang):
        """Sends scaling factor for mapping measurement to scale"""
        return self._make_fieldvalues(maxvalue=str(self._maxvalue), minvalue=str(self._minvalue))


    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<g>  <!-- with widget id and class widget_class, and transform attribute if given -->
  <rect /> <!-- the scale rectangle -->
  <!-- lines and text dependent on the input scale values -->
  <polygon /> <!-- the arrow, with translate linked to the input value -->
</g>"""




class Traditional1(Widget):

    # This class does not display any error messages
    display_errors = False

    _points = ((24,1), (25,1), (49,50), (49,52), (30,52), (30,198), (19,198), (19,52), (1,52), (1,50))

    arg_descriptions = {
                        'transform':FieldArg("text", "translate(10,10)", jsonset=True),
                        'minimum':FieldArg("text", "0"),
                        'maximum':FieldArg("text", "100"),
                        'smallintervals':FieldArg("text", "10"),
                        'largeintervals':FieldArg("text", "20"),
                        'arrow_stroke':FieldArg("text", "grey", jsonset=True),
                        'measurement':FieldArg("text", "50", jsonset=True),
                        'font_family':FieldArg("text", "arial")
                       }


    def _make_scale(self, minimum, maximum, smallintervals, largeintervals):
        "Returns two lists of Decimal values"

        minvalue = Decimal(minimum)
        maxvalue = Decimal(maximum)
        smallint = Decimal(smallintervals)
        largeint = Decimal(largeintervals)
       
        # start at the bottom of the scale with minvalue
        minscale = [minvalue]
        maxscale = [minvalue]
        mns = minvalue
        mxs = minvalue

        while mxs < maxvalue:
            mxs += largeint
            maxscale.append(mxs)

        while True:
            mns += smallint
            if mns > maxscale[-1]:
                break
            minscale.append(mns)
        return minscale, maxscale

    def __init__(self, name=None, brief='', **field_args):
        """A g element which holds the scale and arrow, held in a 400 high x 700 wide space"""
        Widget.__init__(self, name=name, tag_name="g", brief=brief, **field_args)

        # A path which holds the curved shape which will contain the meter

        # the angle of the white backing is 140 degrees, this makes an
        # angle of 20 degrees to the horizonta. So get this in radians
        back_horizontal_angle = math.radians(20.0)

        # The scale

        # the angle of the scale, 120 degrees
        scale_angle = 120
        self._scale_angle = Decimal(scale_angle)

        # the angle to the horizontal, 30 degrees, get it in radians
        scale_horizontal_angle = math.radians((180-scale_angle)/2.0)

        # radius of outside of white backing shape
        r1 = 320

        # radius of scale line
        r2 = 230
        self._scale_r = r2

        # radius of inside of white backing shape
        r3 = 200

        # coordinates of rotation centre of the meter
        cx = 350
        cy = 350
        self._cx = cx
        self._cy = cy

        # create white backing shape
        left_out_x = cx - r1*math.cos(back_horizontal_angle)
        left_out_y = cy - r1*math.sin(back_horizontal_angle)

        right_out_x = cx + r1*math.cos(back_horizontal_angle)
        right_out_y = left_out_y

        right_in_x = cx + r3*math.cos(back_horizontal_angle)
        right_in_y = cy - r3*math.sin(back_horizontal_angle)

        left_in_x = cx - r3*math.cos(back_horizontal_angle)
        left_in_y = right_in_y

        path_data = """
M %s %s
A %s %s 0 0 1 %s %s
L %s %s
A %s %s 0 0 0 %s %s
Z""" % (left_out_x, left_out_y,
        r1, r1, right_out_x, right_out_y,
        right_in_x, right_in_y,
        r3, r3, left_in_x, left_in_y)

        self[0] = tag.ClosedPart(tag_name='path',
                                 attribs={"fill":"white", "stroke":"black", "stroke-width":"1", "d":path_data})

        # create the scale curve

        # still centred on cx, cy
        scale_left_x = cx - r2 * math.cos(scale_horizontal_angle)
        scale_left_y = cy - r2 * math.sin(scale_horizontal_angle)
        scale_right_x = cx + r2 * math.cos(scale_horizontal_angle)
        scale_right_y = scale_left_y

        # Draw the scale curve
        scale_data = """
M %s %s
A %s %s 0 0 1 %s %s
""" % (scale_left_x, scale_left_y,
       r2, r2, scale_right_x, scale_right_y,)

        self[1] = tag.ClosedPart(tag_name='path',
                                 attribs={ "fill":"none", "stroke":"black", "stroke-width":"2", "d":scale_data})


        # The arrow points
        arrow_points = ""
        # move all points to the right and down,
        # note 24.5 is x distance to arrow point
        x_move = cx - 24.5
        # moves arrow down to just touch the scale
        y_move = cy - r2
        for p in self._points:
            point = "%s, %s " % (p[0] + x_move, p[1] + y_move)
            arrow_points += point
        self[2] = tag.ClosedPart(tag_name='polygon', attribs={
                                                           "fill":"black",
                                                           "stroke":"grey",
                                                           "stroke-width":"2",
                                                           "points":arrow_points })

        # insert a circle at arrow hub, of radius 40
        self[3] = tag.ClosedPart(tag_name='circle', attribs={
                                                           "cx": str(cx),
                                                           "cy": str(cy),
                                                           "r": "40",
                                                           "fill":"black",
                                                           "stroke":"grey",
                                                           "stroke-width":"2" })



    def _build(self, page, ident_list, environ, call_data, lang):
        if self.get_field_value("transform"):
            self.update_attribs({"transform":self.get_field_value("transform")})

        font_family = self.get_field_value("font_family")
        if not font_family:
            font_family = "arial"

        if self.get_field_value("arrow_stroke"):
            self[2].update_attribs({"stroke":self.get_field_value("arrow_stroke")})
            self[3].update_attribs({"stroke":self.get_field_value("arrow_stroke")})
        # make the scale
        minscale, maxscale = self._make_scale(self.get_field_value("minimum"),
                                              self.get_field_value("maximum"),
                                              self.get_field_value("smallintervals"),
                                              self.get_field_value("largeintervals"))

        # start angle is 180 - 120 / 2 normally 30
        start_angle = (Decimal('180') - self._scale_angle)/Decimal('2')

        # small lines, each of length 20
        minitems = len(minscale)
        scalemindegs = self._scale_angle / (minitems-1)
        line_r = self._scale_r + 20
        n = 4
        for index, item in enumerate(minscale):
            angle = start_angle + index*scalemindegs
            rads = math.radians(float(angle))

            x1 = self._cx - self._scale_r * math.cos(rads)
            y1 = self._cy - self._scale_r * math.sin(rads)
            x2 = self._cx - line_r * math.cos(rads)
            y2 = self._cy - line_r * math.sin(rads)

            self[n] = tag.ClosedPart(tag_name='line', attribs={
                                                            'x1':str(x1),
                                                            'y1':str(y1),
                                                            'x2':str(x2),
                                                            'y2':str(y2),
                                                            'stroke':"black",
                                                            'stroke-width':"1"  })
            n += 1

        # large lines, each of length 40
        maxitems = len(maxscale)
        scalemaxdegs = self._scale_angle / (maxitems-1)
        line_r = self._scale_r + 40
        # slightly shorter r as the curved line has stroke width of 2
        reduced_r = self._scale_r - 1
        for index, item in enumerate(maxscale):
            angle = start_angle + index*scalemaxdegs
            rads = math.radians(float(angle))

            x1 = self._cx - reduced_r * math.cos(rads)
            y1 = self._cy - reduced_r * math.sin(rads)
            x2 = self._cx - line_r * math.cos(rads)
            y2 = self._cy - line_r * math.sin(rads)

            self[n] = tag.ClosedPart(tag_name='line', attribs={
                                                            'x1':str(x1),
                                                            'y1':str(y1),
                                                            'x2':str(x2),
                                                            'y2':str(y2),
                                                            'stroke':"black",
                                                            'stroke-width':"3"  })
            n += 1
            self[n] = tag.Part(tag_name='text', text=str(item), attribs={
                                                            'x':str(x2-10),
                                                            'y': str(y2-5),
                                                            'font-size': '20',
                                                            'font-family': font_family,
                                                            'stroke':"black",
                                                            'stroke-width':"1"  })

            n += 1

        # now place arrow at the measurement point
        measurement = Decimal(self.get_field_value("measurement"))
        self._minvalue = maxscale[0]
        self._maxvalue = maxscale[-1]
        centre_string = " " + str(self._cx) + " " + str(self._cy) + ")"
        if measurement >= self._maxvalue:
            self[2].update_attribs({"transform" : "rotate(" + str(self._scale_angle/2) + centre_string})
            return
        if measurement <= self._minvalue:
            self[2].update_attribs({"transform" : "rotate(-" + str(self._scale_angle/2) + centre_string})
            return

        measurement_angle = (measurement - self._minvalue)*self._scale_angle/(self._maxvalue-self._minvalue) - self._scale_angle/2

        rotate_string = "rotate(" + str(measurement_angle) + centre_string
        self[2].update_attribs({"transform" : rotate_string})


    def _build_js(self, page, ident_list, environ, call_data, lang):
        """Sends scaling factor for mapping measurement to scale"""
        return self._make_fieldvalues(maxvalue=str(self._maxvalue), minvalue=str(self._minvalue))


    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<g>  <!-- with widget id and class widget_class, and transform attribute if given -->
  <path /> <!-- the white backing arc of the scale -->
  <path /> <!-- the scale curved line -->
  <polygon /> <!-- the arrow, with rotation linked to the measurement -->
  <circle /> <!-- the hub of the arrow -->
  <!-- lines and text giving the scale values -->
</g>"""



class Angle(Widget):
    """An svg compass-like angle meter, fitting in a 500x500 space
       Being a circle with scale or either 24, 100 or 360 and arrow
    """

    # This class does not display any error messages
    display_errors = False

    arg_descriptions = {'transform':FieldArg("text", "", jsonset=True),
                        'font_family':FieldArg("text", "arial"),
                        'measurement':FieldArg("text", "0", jsonset=True),
                        'scale_units':FieldArg("text", "360"),
                       }

    def __init__(self, name=None, brief='', **field_args):
        """A g element which holds the compass, held in a 500 high x 500 wide space"""
        Widget.__init__(self, name=name, tag_name="g", brief=brief, **field_args) 
        # insert a circle at arrow hub, of radius 240
        self[0] = tag.ClosedPart(tag_name='circle', attribs={
                                                       "cx": "250",
                                                       "cy": "250",
                                                       "r": "240",
                                                       "fill":"white",
                                                       "stroke":"black",
                                                       "stroke-width":"4" })

        self[1] = tag.ClosedPart(tag_name='circle', attribs={
                                                       "cx": "250",
                                                       "cy": "250",
                                                       "r": "200",
                                                       "fill":"white",
                                                       "stroke":"black",
                                                       "stroke-width":"2" })

        self[2] = tag.ClosedPart(tag_name='circle', attribs={
                                                       "cx": "250",
                                                       "cy": "250",
                                                       "r": "30",
                                                       "fill":"black",
                                                       "stroke":"black",
                                                       "stroke-width":"2" })

        self[3] = tag.ClosedPart(tag_name='polygon', attribs={
                                                           "fill":"black",
                                                           "stroke":"black",
                                                           "stroke-width":"2",
                                                           "points": "250,65 280,120 260,120 260,400, 240,400 240,120, 220,120" })


    def _build(self, page, ident_list, environ, call_data, lang):
        "create compass"                  
        if self.get_field_value("transform"):
            self.update_attribs({"transform":self.get_field_value("transform")})
        font_family = self.get_field_value("font_family")
        if not font_family:
            font_family = "arial"
        self._scale_units = self.get_field_value("scale_units")
        measurement = Decimal(self.get_field_value("measurement"))
        rotate_string = ''
        if self._scale_units == '24':
            self._draw_24(font_family)
            # now place arrow at the measurement point
            if (measurement > 0) and (measurement < 24):
                rotate_string = "rotate(" + str(measurement*15) + " 250 250)"
        elif self._scale_units == '100':
            self._draw_100(font_family)
            # now place arrow at the measurement point
            if (measurement > 0) and (measurement < 100):
                rotate_string = "rotate(" + str(measurement*Decimal("3.6")) + " 250 250)"
        else:
            self._scale_units = '360'
            self._draw_360(font_family)
            # now place arrow at the measurement point
            if (measurement > 0) and (measurement < 360):
                rotate_string = "rotate(" + str(measurement) + " 250 250)"
        if rotate_string:
            self[3].update_attribs({"transform" : rotate_string})


    def _draw_24(self, font_family):
        "Draw a 24 hr scale"
        for angle in range(0,24):
            if angle:
                rotate_string = "rotate(" + str(angle*15) + " 250 250)"
                # two digit characters moved to the left a bit more than single digits
                if angle < 10:
                    x = '245'
                else:
                    x = '239'
                self.append( tag.Part(tag_name='text', text=str(angle), attribs={
                                                                'x':x,
                                                                'y': '30',
                                                                'font-size': '20',
                                                                'font-family': font_family,
                                                                'stroke':"black",
                                                                'stroke-width':"1",
                                                                'transform' : rotate_string  })  )
                # major lines
                self.append( tag.ClosedPart(tag_name='line', attribs={
                                                            'x1':'250',
                                                            'y1':'40',
                                                            'x2':'250',
                                                            'y2':'55',
                                                            'stroke':"black",
                                                            'stroke-width':"2",
                                                            'transform' : rotate_string  })  )
                for n in range(1,4):
                    # minor lines
                    minor_rotate = "rotate(" + str(angle*15+n*3.75) + " 250 250)"
                    self.append( tag.ClosedPart(tag_name='line', attribs={
                                                                'x1':'250',
                                                                'y1':'40',
                                                                'x2':'250',
                                                                'y2':'50',
                                                                'stroke':"black",
                                                                'stroke-width':"1",
                                                                'transform' : minor_rotate  })  )
            else:
                self.append( tag.Part(tag_name='text', text="24", attribs={
                                                                'x':'239',
                                                                'y': '30',
                                                                'font-size': '20',
                                                                'font-family': font_family,
                                                                'stroke':"black",
                                                                'stroke-width':"1"  })  )
                self.append( tag.ClosedPart(tag_name='line', attribs={
                                                            'x1':'250',
                                                            'y1':'40',
                                                            'x2':'250',
                                                            'y2':'55',
                                                            'stroke':"black",
                                                            'stroke-width':"2"  })  )
                for n in range(1,4):
                    # minor lines
                    minor_rotate = "rotate(" + str(n*3.75) + " 250 250)"
                    self.append( tag.ClosedPart(tag_name='line', attribs={
                                                                'x1':'250',
                                                                'y1':'40',
                                                                'x2':'250',
                                                                'y2':'50',
                                                                'stroke':"black",
                                                                'stroke-width':"1",
                                                                'transform' : minor_rotate  })  )


    def _draw_100(self, font_family):
        "Draw a 100 hr scale"
        for angle in range(0,100,10):
            if angle:
                rotate_string = "rotate(" + str(angle*3.6) + " 250 250)"
                # two digit characters moved to the left a bit more than single digits
                if angle < 10:
                    x = '245'
                else:
                    x = '239'
                self.append( tag.Part(tag_name='text', text=str(angle), attribs={
                                                                'x':x,
                                                                'y': '30',
                                                                'font-size': '20',
                                                                'font-family': font_family,
                                                                'stroke':"black",
                                                                'stroke-width':"1",
                                                                'transform' : rotate_string  })  )
                # major lines
                self.append( tag.ClosedPart(tag_name='line', attribs={
                                                            'x1':'250',
                                                            'y1':'40',
                                                            'x2':'250',
                                                            'y2':'55',
                                                            'stroke':"black",
                                                            'stroke-width':"2",
                                                            'transform' : rotate_string  })  )
                for n in range(2,10,2):
                    # minor lines
                    minor_rotate = "rotate(" + str((angle+n)*3.6) + " 250 250)"
                    self.append( tag.ClosedPart(tag_name='line', attribs={
                                                                'x1':'250',
                                                                'y1':'40',
                                                                'x2':'250',
                                                                'y2':'50',
                                                                'stroke':"black",
                                                                'stroke-width':"1",
                                                                'transform' : minor_rotate  })  )
                for n in range(1,11,2):
                    # mini lines
                    mini_rotate = "rotate(" + str((angle+n)*3.6) + " 250 250)"
                    self.append( tag.ClosedPart(tag_name='line', attribs={
                                                                'x1':'250',
                                                                'y1':'45',
                                                                'x2':'250',
                                                                'y2':'50',
                                                                'stroke':"black",
                                                                'stroke-width':"1",
                                                                'transform' : mini_rotate  })  )
            else:
                self.append( tag.Part(tag_name='text', text="0", attribs={
                                                                'x':'245',
                                                                'y': '30',
                                                                'font-size': '20',
                                                                'font-family': font_family,
                                                                'stroke':"black",
                                                                'stroke-width':"1"  })  )
                self.append( tag.ClosedPart(tag_name='line', attribs={
                                                            'x1':'250',
                                                            'y1':'40',
                                                            'x2':'250',
                                                            'y2':'55',
                                                            'stroke':"black",
                                                            'stroke-width':"2"  })  )
                for n in range(2,10,2):
                    # minor lines
                    minor_rotate = "rotate(" + str(n*3.6) + " 250 250)"
                    self.append( tag.ClosedPart(tag_name='line', attribs={
                                                                'x1':'250',
                                                                'y1':'40',
                                                                'x2':'250',
                                                                'y2':'50',
                                                                'stroke':"black",
                                                                'stroke-width':"1",
                                                                'transform' : minor_rotate  })  )
                for n in range(1,11,2):
                    # mini lines
                    mini_rotate = "rotate(" + str(n*3.6) + " 250 250)"
                    self.append( tag.ClosedPart(tag_name='line', attribs={
                                                                'x1':'250',
                                                                'y1':'45',
                                                                'x2':'250',
                                                                'y2':'50',
                                                                'stroke':"black",
                                                                'stroke-width':"1",
                                                                'transform' : mini_rotate  })  )

    def _draw_360(self, font_family):
        "Draw a 360 hr scale"
        for angle in range(0,360,15):
            if angle:
                rotate_string = "rotate(" + str(angle) + " 250 250)"
                # two digit characters moved to the left a bit more than single digits
                if angle < 10:
                    x = '245'
                if angle < 100:
                    x = '239'
                else:
                    x = '233'
                self.append( tag.Part(tag_name='text', text=str(angle), attribs={
                                                                'x':x,
                                                                'y': '30',
                                                                'font-size': '20',
                                                                'font-family': font_family,
                                                                'stroke':"black",
                                                                'stroke-width':"1",
                                                                'transform' : rotate_string  })  )
                # major lines
                self.append( tag.ClosedPart(tag_name='line', attribs={
                                                            'x1':'250',
                                                            'y1':'40',
                                                            'x2':'250',
                                                            'y2':'55',
                                                            'stroke':"black",
                                                            'stroke-width':"2",
                                                            'transform' : rotate_string  })  )
                for n in range(5,15,5):
                    # minor lines
                    minor_rotate = "rotate(" + str(angle+n) + " 250 250)"
                    self.append( tag.ClosedPart(tag_name='line', attribs={
                                                                'x1':'250',
                                                                'y1':'40',
                                                                'x2':'250',
                                                                'y2':'50',
                                                                'stroke':"black",
                                                                'stroke-width':"1",
                                                                'transform' : minor_rotate  })  )
            else:
                self.append( tag.Part(tag_name='text', text="0", attribs={
                                                                'x':'245',
                                                                'y': '30',
                                                                'font-size': '20',
                                                                'font-family': font_family,
                                                                'stroke':"black",
                                                                'stroke-width':"1"  })  )
                self.append( tag.ClosedPart(tag_name='line', attribs={
                                                            'x1':'250',
                                                            'y1':'40',
                                                            'x2':'250',
                                                            'y2':'55',
                                                            'stroke':"black",
                                                            'stroke-width':"2"  })  )
                for n in range(5,15,5):
                    # minor lines
                    minor_rotate = "rotate(" + str(n) + " 250 250)"
                    self.append( tag.ClosedPart(tag_name='line', attribs={
                                                                'x1':'250',
                                                                'y1':'40',
                                                                'x2':'250',
                                                                'y2':'50',
                                                                'stroke':"black",
                                                                'stroke-width':"1",
                                                                'transform' : minor_rotate  })  )

    def _build_js(self, page, ident_list, environ, call_data, lang):
        """Sends scaling factor for mapping measurement to scale"""
        return self._make_fieldvalues(scale_units=self._scale_units)


    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<g>  <!-- with widget id and class widget_class, and transform attribute if given -->
  <circle /> <!-- the compass circle -->
  <!-- with further scale and arrow contents -->
</g>"""



