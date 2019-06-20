

import math, datetime

from decimal import Decimal

from .. import tag

from . import Widget, ClosedWidget, FieldArg, FieldArgList, FieldArgTable, FieldArgDict


class Chart1(Widget):

    # This class does not display any error messages
    display_errors = False


    arg_descriptions = {
                        'transform':FieldArg("text", "", jsonset=True),
                        'values':FieldArgList('integer', jsonset=True),
                        'stroke_width':FieldArg("integer", 1),
                        'stroke':FieldArg("text", "black"),
                        'plus50legend':FieldArg("text", ""),
                        'minus50legend':FieldArg("text", ""),
                        'zerolegend':FieldArg("text", ""),
                        'font_family':FieldArg("text", "arial")
                       }


    def __init__(self, name=None, brief='', **field_args):
        """A g element which holds a chart, held in a 200 high x 500 wide space
           The vertical scale is +100 to -100
           values: a list of integers, each integer should be between -100 and +100
           with a maximum of fifty integers.
           These will be plotted on the chart at 10point intervals, with the
           last point on the right of the chart
        """
        Widget.__init__(self, name=name, tag_name="g", brief=brief, **field_args)
        self[0] = tag.ClosedPart(tag_name='rect', attribs={"x":"0",
                                                           "y":"0",
                                                           "width":"500",
                                                           "height":"200",
                                                           "fill":"white",
                                                           "stroke":"green",
                                                           "stroke-width":"1"})
        # centre line
        self[1] = tag.ClosedPart(tag_name='line', attribs={"x1":"0",
                                                           "y1":"100",
                                                           "x2":"500",
                                                           "y2":"100",
                                                           "stroke":"green",
                                                           "stroke-width":"3"})

        # 50 lines - horizontal
        self[2] = tag.ClosedPart(tag_name='line', attribs={"x1":"0",
                                                           "y1":"50",
                                                           "x2":"500",
                                                           "y2":"50",
                                                           "stroke":"green",
                                                           "stroke-width":"1"})
        self[3] = tag.ClosedPart(tag_name='line', attribs={"x1":"0",
                                                           "y1":"150",
                                                           "x2":"500",
                                                           "y2":"150",
                                                           "stroke":"green",
                                                           "stroke-width":"1"})
        # 50 lines - vertical
        for n in range(50, 500, 50):
            self.append(tag.ClosedPart(tag_name='line', attribs={"x1":str(n),
                                                                 "y1":"0",
                                                                 "x2":str(n),
                                                                 "y2":"200",
                                                                 "stroke":"green",
                                                                 "stroke-width":"1"}))


    def _build(self, page, ident_list, environ, call_data, lang):
        if self.get_field_value("transform"):
            self.update_attribs({"transform":self.get_field_value("transform")})

        font_family = self.get_field_value("font_family")
        if not font_family:
            font_family = "arial"

        if self.get_field_value("plus50legend"):
            charnumbers = len(self.get_field_value("plus50legend"))
            textlength = 5*charnumbers
            self.append(tag.ClosedPart(tag_name='rect', attribs={"x":"3",
                                                           "y":"40",
                                                           "width":str(textlength+10),
                                                           "height":"20",
                                                           "fill":"white",
                                                           "stroke-width":"0"}))
            self.append( tag.Part(tag_name='text',
                                  text=self.get_field_value("plus50legend"),
                                  attribs={
                                            'x':"5",
                                            'y':"53",
                                            'font-size': '10',
                                            'font-family': font_family,
                                            'lengthAdjust':"spacingAndGlyphs",
                                            'textLength':str(textlength),
                                            'fill':"green",
                                            'stroke-width':"0"  }))

        if self.get_field_value("minus50legend"):
            charnumbers = len(self.get_field_value("minus50legend"))
            textlength = 5*charnumbers
            self.append(tag.ClosedPart(tag_name='rect', attribs={"x":"3",
                                                           "y":"140",
                                                           "width":str(textlength+10),
                                                           "height":"20",
                                                           "fill":"white",
                                                           "stroke-width":"0"}))
            self.append( tag.Part(tag_name='text',
                                  text=self.get_field_value("minus50legend"),
                                  attribs={
                                            'x':"5",
                                            'y':"153",
                                            'font-size': '10',
                                            'font-family': font_family,
                                            'lengthAdjust':"spacingAndGlyphs",
                                            'textLength':str(textlength),
                                            'fill':"green",
                                            'stroke-width':"0"  }))


        if self.get_field_value("zerolegend"):
            charnumbers = len(self.get_field_value("zerolegend"))
            textlength = 5*charnumbers
            self.append(tag.ClosedPart(tag_name='rect', attribs={"x":"3",
                                                           "y":"90",
                                                           "width":str(textlength+10),
                                                           "height":"20",
                                                           "fill":"white",
                                                           "stroke-width":"0"}))
            self.append( tag.Part(tag_name='text',
                                  text=self.get_field_value("zerolegend"),
                                  attribs={
                                            'x':"5",
                                            'y':"103",
                                            'font-size': '10',
                                            'font-family': font_family,
                                            'lengthAdjust':"spacingAndGlyphs",
                                            'textLength':str(textlength),
                                            'fill':"green",
                                            'stroke-width':"0"  }))

        stroke_width = self.get_field_value("stroke_width")
        if not stroke_width:
            stroke_width = "1"
        else:
            stroke_width = str(stroke_width)

        stroke = self.get_field_value("stroke")
        if not stroke:
            stroke = "black"

        values = self.get_field_value("values")
        if not values:
            # still include a polyline tag, for javascript to find
            self.append(tag.ClosedPart(tag_name='polyline', attribs={"points":"",
                                                                     "fill":"none",
                                                                     "stroke":stroke,
                                                                     "stroke-width":stroke_width}))

            return

        vals = list(reversed(values))

        xpoint = 510
        points = ""
        for ypoint in vals:
            xpoint = xpoint-10
            if xpoint < 0:
                break
            if ypoint > 100:
                y = "0"
            elif ypoint < -100:
                y = "200"
            else:
                y = str(100-ypoint)
            points = points + " " + str(xpoint) + "," + y

        self.append(tag.ClosedPart(tag_name='polyline', attribs={"points":points,
                                                                 "fill":"none",
                                                                 "stroke":stroke,
                                                                 "stroke-width":stroke_width}))

    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<g>  <!-- with widget id and class widget_class, and transform attribute if given -->
  <rect /> <!-- the chart rectangle -->
  <!-- lines and text which draw the chart -->
  <polyline /> <!-- Draws the values on the chart -->
</g>"""




class Graph48Hr(Widget):

    # This class does not display any error messages
    display_errors = False


    arg_descriptions = {
                        'transform':FieldArg("text", "", jsonset=True),
                        'values':FieldArgTable(('text', 'datetime')),
                        'fill':FieldArg("text", "white"),
                        'fill_opacity':FieldArg("text", "1"),
                        'plotcol':FieldArg("text", "black"),
                        'font_family':FieldArg("text", "arial"),
                        'axiscol':FieldArg("text", "green"),
                        'minvalue':FieldArg("text", "0"),
                        'maxvalue':FieldArg("text", "100"),
                        'last_day':FieldArg("date", "")
                       }


    def __init__(self, name=None, brief='', **field_args):
        """A g element which holds a graph, held in a 1200 high x 1200 wide space
           values: a list of datetime objects covering a 48 hr period
           These will be plotted on the chart to the latest date in the values
           If last_day given, rightmost axis will be midnight of that day 
        """
        Widget.__init__(self, name=name, tag_name="g", brief=brief, **field_args)
        self._hr = datetime.timedelta(hours=1)
        self._axiscol = "green"
        self._plotcol = "black"
        self._font_family = "arial"


    def _build(self, page, ident_list, environ, call_data, lang):
        if self.get_field_value("transform"):
            self.update_attribs({"transform":self.get_field_value("transform")})

        fill = self.get_field_value("fill")
        if not fill:
            fill = "white"

        fill_opacity = self.get_field_value("fill_opacity")
        if not fill_opacity:
            fill_opacity = "0"

        self._font_family = self.get_field_value("font_family")
        if not self._font_family:
            self._font_family = "arial"

        self._axiscol = self.get_field_value("axiscol")
        if not self._axiscol:
            self._axiscol = "green"

        self._plotcol = self.get_field_value("plotcol")
        if not self._plotcol:
            self._plotcol = "black"

        self[0] = tag.ClosedPart(tag_name='rect', attribs={"x":"240",
                                                           "y":"20",
                                                           "width":"960",
                                                           "height":"720",
                                                           "fill":fill,
                                                           "fill-opacity":fill_opacity,
                                                           "stroke":self._axiscol,
                                                           "stroke-width":"1"})

        values = self.get_field_value("values")
        last_day = self.get_field_value("last_day")

        if (not values) and (not last_day):
            # do not know when to plot
            return

        # get maxt the last datetime to plot
        if last_day:
            # set maxt at midnight of last_day
            maxt = datetime.datetime(last_day.year, last_day.month, last_day.day) + datetime.timedelta(days=1)
        else:
            # set maxt as the start of the hour after the last plotted value
            maxt = values[0][1]
            for valpair in values:
                val, t = valpair
                # t is a datetime object
                if t > maxt:
                    maxt = t
            maxt = maxt.replace(minute=0, second=0, microsecond=0) + self._hr

        mint = maxt - datetime.timedelta(days=2)

        axist = mint
        for h in range(0,49):
            x = str(240 + h*20)
            if (axist.hour == 6) or (axist.hour == 18):
                if (h>0) and (h<48):
                    self.append(tag.ClosedPart(tag_name='line', attribs={"x1":x,
                                                                         "y1":"740",
                                                                         "x2":x,
                                                                         "y2":"720",
                                                                         "stroke":self._axiscol,
                                                                         "stroke-width":"1"}))
            elif axist.hour == 12:
                if (h>0) and (h<48):
                    self.append(tag.ClosedPart(tag_name='line', attribs={"x1":x,
                                                                         "y1":"740",
                                                                         "x2":x,
                                                                         "y2":"715",
                                                                         "stroke":self._axiscol,
                                                                         "stroke-width":"1"}))
                self.append(tag.Part(tag_name='text', text="12:00", attribs={
                                                            'x':str(215 + h*20),
                                                            'y': "770",
                                                            'font-size': '20',
                                                            'font-family': self._font_family,
                                                            'fill':self._axiscol,
                                                            'stroke-width':"0"  }))
            elif axist.hour == 0:
                if (h>0) and (h<48):
                    self.append(tag.ClosedPart(tag_name='line', attribs={"x1":x,
                                                                         "y1":"740",
                                                                         "x2":x,
                                                                         "y2":"710",
                                                                         "stroke":self._axiscol,
                                                                         "stroke-width":"2"}))
                self.append(tag.Part(tag_name='text', text=axist.strftime("%d %b"), attribs={
                                                            'x':str(215 + h*20),
                                                            'y': "770",
                                                            'font-size': '20',
                                                            'font-family': self._font_family,
                                                            'fill':self._axiscol,
                                                            'stroke-width':"0"  }))
                self.append(tag.Part(tag_name='text', text="00:00", attribs={
                                                            'x':str(215 + h*20),
                                                            'y': "790",
                                                            'font-size': '20',
                                                            'font-family': self._font_family,
                                                            'fill':self._axiscol,
                                                            'stroke-width':"0"  }))

            elif (h>0) and (h<48):
                self.append(tag.ClosedPart(tag_name='line', attribs={"x1":x,
                                                                     "y1":"740",
                                                                     "x2":x,
                                                                     "y2":"730",
                                                                     "stroke":self._axiscol,
                                                                     "stroke-width":"1"}))

            axist = axist + self._hr

        # create Y axis
        minv = self.get_field_value("minvalue")
        maxv = self.get_field_value("maxvalue")

        isint = True
        try: 
            int_minv = int(minv)
        except ValueError:
            isint = False
        if isint:
            try: 
                int_maxv = int(maxv)
            except ValueError:
                isint = False

        if isint and (int_maxv > int_minv+4):
            # create a Y axis of integer values
            int_maxv, str_minv, str_maxv = self._integer_axis(int_maxv, int_minv)
        else:
            int_maxv, str_minv, str_maxv = self._float_axis(float(maxv), float(minv))

        ymin = Decimal(str_minv)
        ymax = Decimal(str_maxv)

        # y = m*val + c
        # m = 720 / (ymax-ymin)
        # c = -m*ymin

        m = Decimal("720") / (ymax-ymin)
        c = -ymin*m

        # for each point, plot a + on the graph
        for valpair in values:
            val, t = valpair
            if t < mint:
                # early point outside plottable range
                continue
            if t > maxt:
                # late point outside plottable range
                continue
            val = Decimal(val)
            if val < ymin:
                # low point outside plottable range
                continue
            if val > ymax:
                # high point outside plottable range
                continue
            tdelta = t-mint
            seconds = tdelta.total_seconds()
            x = int(960 * seconds / 172800)
            y = int(m*val + c)
            self._plot_cross(x, y)


    def _plot_cross(self, x, y):
        "plot a + on the graph at x, y"
        # Vertical line
        self.append(tag.ClosedPart(tag_name='line', attribs={"x1":str(240+x),
                                                             "y1":str(735-y),
                                                             "x2":str(240+x),
                                                             "y2":str(745-y),
                                                             "stroke":self._plotcol,
                                                             "stroke-width":"1"}))
        # Horizontal line
        self.append(tag.ClosedPart(tag_name='line', attribs={"x1":str(235+x),
                                                             "y1":str(740-y),
                                                             "x2":str(245+x),
                                                             "y2":str(740-y),
                                                             "stroke":self._plotcol,
                                                             "stroke-width":"1"}))

    def _float_axis(self, maxv, minv):
        "create a Y axis of float values, return new int_maxv, str_minv, str_maxv"
        if minv == 0.0:
            # convert 0.0045 to 45
            # convert 4500.0 to 45
            tens = math.floor(math.log10(abs(maxv)))-1
            maxy = math.ceil(maxv/10**tens)
            return self._integer_axis(maxy, 0, tens)
        else:
            diff = maxv - minv
            tens = math.floor(math.log10(abs(diff)))-1
            maxy = math.ceil(maxv/10**tens)
            miny = math.floor(minv/10**tens)
            return self._integer_axis(maxy, miny, tens)



    def _integer_axis(self, int_maxv, int_minv, tens=0):
        "create a Y axis of integer values, if necessary increase int_maxv, return new int_maxv, str_minv, str_maxv"
        # diff is the difference between minimum and maximum, divide it into intervals
        # the number of intervals should also divide 720 pixels nicely, i.e. 16, 15, 12, 10, 9, 8, 6, 5
        diff = int_maxv - int_minv

        # order of prefferred interval spacing
        prefferred = (5, 10, 2, 15, 4, 25, 20)

        difftens = math.floor(math.log10(diff))

        if difftens>2:
            prefferred = ( item * 10**(difftens-1) for item in prefferred)

        number_of_intervals = 0
        for i in prefferred:
            if (diff % i == 0) and (diff//i in (16, 15, 12, 10, 9, 8, 6, 5)):
                # intervals with spacing of i is given priority
                number_of_intervals = diff//i
                break

        if not number_of_intervals:
            if diff % 16 == 0:
                # divide axis by sixteen
                number_of_intervals = 16
            elif diff % 15 == 0:
                # divide axis by fifteen
                number_of_intervals = 15
            elif diff % 12 == 0:
                # divide axis by twelve
                number_of_intervals = 12
            elif diff % 10 == 0:
                # divide axis by ten
                number_of_intervals = 10
            elif diff % 9 == 0:
                # divide axis by nine
                number_of_intervals = 9
            elif diff % 8 == 0:
                # divide axis by eight
                number_of_intervals = 8
            elif diff % 6 == 0:
                # divide axis by six
                number_of_intervals = 6
            elif diff % 5 == 0:
                # divide axis by five
                number_of_intervals = 5
            else:
                # None of the above go nicely into diff, so add 1 to int_maxv and try again
                return self._integer_axis(int_maxv+1, int_minv, tens)

        if tens:
            mult = Decimal("1e" + str(tens))
            if abs(tens)>3:
                fstring = "0.4g"
            elif tens<0:
                fstring = "0." + str(abs(tens)) + "f"
            else:
                fstring = "0.2f"
        else:
            mult = 1
            fstring = ''

        # put the maximum value at the top of the axis
        str_maxv = format(int_maxv*mult, fstring)
        self.append(tag.Part(tag_name='text', text=str_maxv, attribs={
                                                                    'x':str(220),
                                                                    'y': "25",
                                                                    'text-anchor':'end',
                                                                    'font-size': '20',
                                                                    'font-family': self._font_family,
                                                                    'fill':self._axiscol,
                                                                    'stroke-width':"0"  }))

        # put the minimum value at the bottom of the axis
        if int_minv:
            str_minv = format(int_minv*mult, fstring)
        else:
            str_minv = "0"
        self.append(tag.Part(tag_name='text', text=str_minv, attribs={
                                                                'x':str(220),
                                                                'y': "745",
                                                                'text-anchor':'end',
                                                                'font-size': '20',
                                                                'font-family': self._font_family,
                                                                'fill':self._axiscol,
                                                                'stroke-width':"0"  }))


        # yval is the axis value at the intervals, so starting from the top
        yval = int_maxv
        y_interval = diff//number_of_intervals
        # pixel_interval is the number of pixels in the interval
        pixel_interval = 720//number_of_intervals
        # with range limits so no line at top and bottem - so rectangle not overdrawn
        for y in range(pixel_interval+20, 740, pixel_interval):
            yval -= y_interval
            self.append(tag.ClosedPart(tag_name='line', attribs={"x1":"240",
                                                                 "y1":str(y),
                                                                 "x2":"260",
                                                                 "y2":str(y),
                                                                 "stroke":self._axiscol,
                                                                 "stroke-width":"1"}))
            self.append(tag.Part(tag_name='text', text=format(yval*mult, fstring), attribs={
                                                                        'x':str(220),
                                                                        'y': str(y+5),
                                                                        'text-anchor':'end',
                                                                        'font-size': '20',
                                                                        'font-family': self._font_family,
                                                                        'fill':self._axiscol,
                                                                        'stroke-width':"0"  }))
        return int_maxv, str_minv, str_maxv



    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<g>  <!-- with widget id and class widget_class, and transform attribute if given -->
  <rect x="240" y="20" height="720" width="960" /> <!-- the axis rectangle -->
  <!-- lines and text which draw the graph -->
</g>"""



class StarChart(Widget):

    # This class does not display any error messages
    display_errors = False


    arg_descriptions = {
                        'transform':FieldArg("text", "", jsonset=True),
                        'fill':FieldArg("text", "white"),
                        'stroke_width':FieldArg("integer", 1),
                        'stroke':FieldArg("text", "black"),
                        'stars':FieldArgTable(('text', 'text', 'text')),   # star diameter, ra, dec
                        'ra':FieldArg("text", "0"),      # right ascension 0 to 360
                        'dec':FieldArg("text", "90"),    # declination 90 to -90
                        'view':FieldArg("text", "180"),  # the field of view
                        'flip_horizontal':FieldArg("boolean", False),
                        'flip_vertical':FieldArg("boolean", False),
                        'cross':FieldArg("boolean", False),
                        'square':FieldArg("boolean", False)
                       }


    def __init__(self, name=None, brief='', **field_args):
        """A g element which holds a circular star chart, held in a 500 high x 500 wide space
        """
        Widget.__init__(self, name=name, tag_name="g", brief=brief, **field_args)
        self[0] = tag.ClosedPart(tag_name='circle', attribs={"cx":"250",
                                                             "cy":"250",
                                                             "r":"250",
                                                             "fill":"white",
                                                             "stroke":"black",
                                                             "stroke-width":"1"})



    def _build(self, page, ident_list, environ, call_data, lang):
        if self.get_field_value("transform"):
            self.update_attribs({"transform":self.get_field_value("transform")})
        stroke_width = self.get_field_value("stroke_width")
        if stroke_width:
            self[0].update_attribs({"stroke-width":str(stroke_width)})
        # stroke will be the star colour
        stroke = self.get_field_value("stroke")
        if not stroke:
            stroke = 'black'
        self[0].update_attribs({"stroke":stroke})
        fill = self.get_field_value("fill")
        if fill:
            self[0].update_attribs({"fill":fill})
        if not self.get_field_value("stars"):
            return

        # limit centre of the chart
        ra0_deg = float(self.get_field_value("ra"))
        if (ra0_deg < 0.0) or (ra0_deg > 360.0):
            ra0_deg = 0.0
        ra0 = math.radians(ra0_deg)

        dec0_deg = float(self.get_field_value("dec"))
        if dec0_deg > 90.0:
            dec0_deg = 90.0
        if dec0_deg < -90.0:
            dec0_deg = -90.0
        dec0 = math.radians(dec0_deg)

        view_deg = float(self.get_field_value("view"))

        # avoid division by zero
        if view_deg < 0.000001:
            view_deg = 0.00001

        # avoid extra wide angle
        if view_deg > 270.0:
            view_deg = 270.0

        max_dec = dec0_deg + view_deg / 2.0
        if max_dec > 90.0:
            max_dec = 90.0

        min_dec = dec0_deg - view_deg / 2.0
        if min_dec < -90.0:
            min_dec = -90.0

        scale = 500 / math.radians(view_deg)

        cosdec0 = math.cos(dec0)
        sindec0 = math.sin(dec0)

        # stereographic algorithm
        # taken from www.projectpluto.com/project.htm


        for star in self.get_field_value("stars"):

            ra_deg = float(star[1])
            dec_deg = float(star[2])

            if (ra_deg < 0.0) or (ra_deg > 360.0):
                # something wrong, do not plot this star
                continue

            # don't calculate star position if its declination is outside required view
            # unfortunately ra is more complicated
            if dec_deg > max_dec:
                continue
            if dec_deg < min_dec:
                continue

            # get the radius of a star circle to plot
            if star[0]:
                radius = float(star[0])/2.0
            else:
                radius = 0.5
            if radius < 0.1:
                radius = 0.1

            ra = math.radians(ra_deg)
            dec = math.radians(dec_deg)
            delta_ra = ra - ra0
            sindec = math.sin(dec)
            cosdec = math.cos(dec)
            cosdelta_ra = math.cos(delta_ra)

            x1 = cosdec * math.sin(delta_ra);
            y1 = sindec * cosdec0 - cosdec * cosdelta_ra * sindec0
            z1 = sindec * sindec0 + cosdec * cosdec0 * cosdelta_ra
            if z1 < -0.9:
               d = 20.0 * math.sqrt(( 1.0 - 0.81) / ( 1.00001 - z1 * z1))
            else:
               d = 2.0 / (z1 + 1.0)
            x = x1 * d * scale
            y = y1 * d * scale

            if x*x + y*y > 62500:
                # star position is outside the circle
                continue

            # move origin to circle centre (250,250)
            if self.get_field_value("flip_horizontal"):
                cx = 250 + x
            else:
                cx = 250 - x
            if self.get_field_value("flip_vertical"):
                cy = 250 + y
            else:
                cy = 250 - y
            self.append(tag.ClosedPart(tag_name='circle', attribs={"cx":str(cx),
                                                                   "cy":str(cy),
                                                                   "r":str(radius),
                                                                   "fill":stroke,
                                                                   "stroke":stroke}))


            if self.get_field_value("square"):
                # plot a square on the chart centre
                self.append(tag.ClosedPart(tag_name='rect', attribs={"x":"240",
                                                                     "y":"240",
                                                                     "width":"20",
                                                                     "height":"20",
                                                                     "style":"stroke:%s;stroke-width:1;fill-opacity:0;" % (stroke,)}))

            if self.get_field_value("cross"):
                # plot a + on the chart centre
                self.append(tag.ClosedPart(tag_name='line', attribs={"x1":"240",
                                                                     "y1":"250",
                                                                     "x2":"260",
                                                                     "y2":"250",
                                                                     "stroke":stroke,
                                                                     "stroke-width":"1"}))
                self.append(tag.ClosedPart(tag_name='line', attribs={"x1":"250",
                                                                     "y1":"240",
                                                                     "x2":"250",
                                                                     "y2":"260",
                                                                     "stroke":stroke,
                                                                     "stroke-width":"1"}))


 
    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<g>  <!-- with widget id and class widget_class, and transform attribute if given -->
  <circle /> <!-- A circle with fill, stroke and stroke width, and diameter 500 -->
  <!-- with multiple 'star' spots, positioned according to the given ra and dec values -->
  <!-- and each with a drawn diameter given per star -->
  <!-- centre cross drawn if cross is True -->
</g>"""

