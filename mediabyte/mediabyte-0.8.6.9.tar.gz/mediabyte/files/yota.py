import re
import copy
import hashlib
from . import bno, yno
from . import bit
from . import srt_search_function as srt
from . import omm_file_parser, sh
from . import lib
import string



def iframe(self, width=360, pause=False, title=False, center=True):
    """Returns IFrame format."""

    url = '<center><iframe width="360" height="216" title="YYYYY" src="XXXXX" frameborder=0 allowfullscreen></iframe></center>'
    if width != 360:
        url = url.replace('360', str(width))
        height = int(width * 0.6)
        url = url.replace('216', str(height))
    newUrl = url.replace('XXXXX', self.url)
    newUrl = newUrl.replace('YYYYY', self.title)
    if pause:
        newUrl = newUrl.replace('autoplay=1','autoplay=0')
    if title:
        new_title = '<center><p>' + repr(self) + '<p>'
        newUrl = newUrl.replace('<center>',new_title)
    if not center:
        newUrl = newUrl[8:-9]
    
    return(newUrl)


def build_html(self):

    if self.tags:
        html_str = '<a href="' + str(self.url) + '" title="' + " ".join(self.tags) +  '">' + str(self.title) + '</a>'
    else:
        html_str = '<a href="' + str(self.url) + '">' + str(self.title) + '</a>'

    try: 
        for item in self.bits:        
            html_str += '  [' + item.html + ']'
    except:
        pass

    return html_str    


def build_bits(bits):

    bits_list = []
    if len(bits) > 1:
        for item in bits:
            bit_object = bno.main(item)
            try:
                bit_object.title 
            except ValueError:
                bit_object.title = 'myBit'
                bit_object.update()
            bits_list.append(bit_object)
    elif len(bits) == 1:
        bit_object = bno.main(bits[0])
        bits_list.append(bit_object)
    return bits_list

class Mixtape():
    """Takes Sample object, returns single item Mixtape.
    Also produced from Sample object addition: sample_obj + sample_obj."""

    def __init__(self, *subclips):

        content_list = []
        for subclip in subclips:
            content_list.append(subclip)

        self.content = content_list
        self.find = {sample.first_name : sample for sample in self.content}


    def __len__(self):
        """Show length in seconds."""

        # combined_length = 0
        # for sample in self.content:
        #     combined_length += len(sample)

        combined_length = len(self.content)

        return(combined_length)


    def open_tabs(self):
        """Open all samples in tabs in browser."""
        result = []
        for item in self:
            new_url = item.url[:-1] + '0'
            result.append(new_url)
        
        lib.Convert._browser_open(*result)


    def __getitem__(self, given):
        
        if isinstance(given, slice):
            # do your handling for a slice object:
            cut_mix = copy.deepcopy(self.content[given])
            new_mix = Mixtape(cut_mix[0])
            for item in cut_mix[1:]:
                new_mix += item
            return(new_mix)
        elif isinstance(given, int):
            # Do your handling for a plain index
            return(self.content[given])


    def __repr__(self):

        yotas_string = ""
        for i, sample in enumerate(self.content):
            yotas_string += str(i) + ". " + sample.title + "\n"

        return(str(yotas_string))


    def __str__(self):
        
        self_str = "\n".join(self.omm())

        return(self_str)


    def html(self, title_string_input=None):
        """Show HTML format string."""

        html_list = [sample.html for sample in self.content]
        if title_string_input:
            title_string_2 = "<h2>" + title_string_input + "</h2> <br> "
        else:
            title_string_2 = "<h2>" + "Mediabyte Mixtape" + "</h2> <br> "

        html_string = title_string_2

        for i, line in enumerate(html_list):
            html_string += str(i) + ". " + line + " <br>"

        return(html_string)


    def append(self, value):

        self.content.append(value)
        self.find[value.first_name] = value


    def __setitem__(self, key, value):

        self.content.__setitem__(key, value)


    def __delitem__(self, key):

        first_name = self.content[key].first_name
        self.content.__delitem__(key)
        del self.find[first_name]


    def __add__(self, value):

        if isinstance(value, Yota) or isinstance(value, Cue) or isinstance(value, Sample) or isinstance(value, bit.Link) or isinstance(value, bit.Mp3):
            self.content.append(value)

        if isinstance(value, Mixtape):
            for item in value.content:
                self.content.append(item)
                self.find[item.first_name] = item
                

        return(self)


    def time(self):
        """Show time in 1h2m3s format."""

        combined_length = 0
        for sample in self.content:
            try:
                combined_length += len(sample)
            except TypeError:
                print('Error: Only Sample-only Mixtapes support the time method at present...')
                return
        if combined_length > (60 * 60):
            hours = int(combined_length / 60 / 60)
            minutes = int(combined_length / 60 - (hours * 60))
            seconds_left = int(combined_length - ((hours * 60 * 60) + (minutes * 60)))
            time_string = str(hours) + 'h' + str(round(minutes, 0)) + "m" + str(seconds_left) + "s"

            return(time_string)

        if combined_length > 59:
            minutes = int(combined_length / 60)
            seconds_left = int(combined_length - (minutes * 60))
            time_string = str(round(minutes, 0)) + "m" + str(seconds_left) + "s"
            return(time_string)


    def methods(self):
        """Show methods and parameters."""

        result = []
        for item in dir(self):
            if item.startswith('__'):
                pass
            else:
                result.append(item)

        return(result)


    def show(self, title_str=None):
        """Show HTML output in Jupyter Notebook."""

        from IPython.display import HTML, display
        display(HTML(self.html(title_str)))


    def iframe(self, width=360, titles=False):
        """Returns chapterized HTML."""

        iframe_collection_str = ""
        for item in self:
            new_url = item.url[:-1] + "0"
            new_str = '<iframe width="' + str(width) + '" height="' + str(int(width * 0.6)) + '" title="' + item.title + '" src="' + new_url + '" frameborder=0 allowfullscreen></iframe>'
            if titles:
                new_str = '<h3>' + repr(item) + '</h3> <br>' + new_str
            iframe_collection_str += new_str + " "
    
        return(iframe_collection_str)


    def player(self, width=360, titles=False):
        """Returns javascript player HTML."""

        iframe_collection_str = ""
        for item in self:
            new_url = item.url[:-1] + "0" + "&enablejsapi=1"
            new_str = '<iframe width="' + str(width) + '" height="' + str(int(width * 0.6)) + '" title="' + item.title + '" src="' + new_url + '" frameborder=0 allowfullscreen></iframe>'
            if titles:
                new_str = '<h3>' + repr(item) + '</h3> <br>' + new_str
            iframe_collection_str += new_str + " "
    

        javascript_by_jonas = """<!DOCTYPE html>
                                <html lang="en">
                                <head>
                                <meta charset="utf-8">
                                <meta name="viewport" content="width=device-width, initial-scale=1">
                                <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
                                <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.0/jquery.min.js"></script>
                                <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js"></script>
                                <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>
                                <title> {{ mediabyte.title }}</title>
                                </head>
                                <body>

                                <script src="https://www.youtube.com/iframe_api"></script><script>function onYouTubeIframeAPIReady() { window.yotasamples = {}; let i = 0;  for (let ifrm of document.getElementsByTagName("iframe")) {       ifrm.id = "sample" + i;      ifrm.yotaidx = i;      window.yotasamples[i] = new YT.Player(ifrm.id, {events: {"onStateChange": playerStateChange}});        i++;  }}  function playerStateChange(event) {    console.log(event.data);    switch(event.data) {        case 0:            let myidx = event.target.getIframe().yotaidx;            event.target.getIframe().classList.remove("current");if (window.yotasamples[myidx+1]) { window.yotasamples[myidx+1].getIframe().classList.add("current");window.yotasamples[myidx+1].playVideo();} else{window.yotasamples[0].getIframe().classList.add("current")}                        break    }  }document.querySelector("iframe").classList.add("current");</script><input type=button style="position:fixed;bottom:0;left:0" value="Toggle View" onclick="document.documentElement.classList.toggle(this.dataset.targetclass);" data-targetclass=julekalenderview><style>html:not(.julekalenderview) iframe:not(.current) {display:none} </style>

                                </body>
                                </html>

                                """

        javascript_by_jonas = javascript_by_jonas.replace("{{ mediabyte.title }}", "YouTube " + self[0].title[:-2])

        iframe_collection_str += javascript_by_jonas

        return(iframe_collection_str)


    def omm(self):
        """Returns omm format string."""

        omm_list = []
        for item in self:
            omm_list.append(item.omm)

        return(omm_list)


    def omm_oneline(self):
        """Returns omm oneline mixtape format."""

        result = ""
        for item in self:
            result += item.omm + "."
        
        result = result[:-1]

        return(result)


    def write_player_html(self, filename, width=360):

        html = self.player(width=width)
        with open(filename,'w') as f:
            f.write(html)
            f.write("\n\n")
        

    def vlc(self):

        def check_mixtape_for_only_yota(mixtape):

            for item in mixtape:
                if not isinstance(item, Yota):
                    return False
            return True

        # check Mixtape only contains Yota objects
        if check_mixtape_for_only_yota(self):
            vlc_str = ""
            url_list = []
            for item in self:
                basic_url = 'https://youtube.com/watch?v=' + item.omm[2:13]
                url_list.append(basic_url)
            sh.ell('vlc', *url_list)
        else:
            raise ValueError('only supported for Yota-only Mixtapes')


    def srt_search(self, search_term, clip_length=10):

        result_list = []
        myMixtape = None
        for item in self:
            result = item.srt_search(search_term, clip_length=clip_length)
            if isinstance(result, Mixtape):
                for item in result:
                    result_list.append(item)
            elif isinstance(result, Sample):
                result_list.append(item)
            elif isinstance(result, Cue) and clip_length:
                print('Error, got Cue object while clip_length:', clip_length)
            elif isinstance(result, Cue):
                result_list.append(item)
        if result_list:
            myMixtape = Mixtape(result_list[0])
            for item in result_list[1:]:
                myMixtape += item
                
        return(myMixtape)


    def write_omm(self, filename):
        with open(filename, 'w') as f:
            for item in self.omm():
                f.write(item)
                f.write("\n")


    def write_omm_oneline(self, filename=None):
        with open(filename, 'w') as f:
            f.write(self.omm_oneline())
            f.write("\n")


    def hash(self):
        m = hashlib.sha256()
        m.update(self.omm_oneline().encode())
        temp_hash = m.hexdigest()

        for i, char in enumerate(temp_hash):
            if char in string.ascii_letters:
                calculated_hash = temp_hash[i:i+11]

                return(calculated_hash)



    def add_tags(self, tags=[]):
        for item in self:
            try:
                item.tags += tags
            except:
                item.tags = tags
            item.update()
        #return mixtapeObj



class Sample():
    """Takes YouTube URL, time tuple (start in secs, end in secs) title (optional), tags (optional),
    returns yota Sample object."""

    def __init__(self, url, time_start=None, time_end=None, title=None, tags=[], bits=[]):

            youtube_hash_match = re.search('[0-9a-zA-Z_\-]{11}', url)   # extract 11-character youtube hash
            self.youtube_hash = youtube_hash_match.group(0)
            self.parent_url = 'https://www.youtube.com/watch?v=' + url
            self.first_name = self.youtube_hash[:3]
            self.middle_name  =  self.youtube_hash[3:7]
            self.last_name = self.youtube_hash[7:]

            if time_start: self.time_start = time_start
            if time_end: self.time_end = time_end
            if title:
                title2 = title.replace("_"," ")
                self.title = title2
            else:
                self.title = ""
            if tags:
                self.tags = tags
            else:
                self.tags = []

            self.url = 'https://www.youtube.com/embed/' + self.youtube_hash + '?start=' + str(self.time_start) + '&end=' + str(self.time_end) + '&rel=0' + '&autoplay=1'


            self.html = build_html(self)

            # omm formatting
            self.omm = 'y.' + self.youtube_hash
            self.omm += '.' + self.youtube_time_format(self.time_start)

            if self.title: self.omm += '.' + self.title.replace(" ", "_")
            if self.tags:
                for tag in self.tags:
                    self.omm += '.' + tag
                if self.omm[-1] == '.':
                    self.omm = self.omm[:-1]
            self.omm += '.' + str(self.youtube_time_format(self.time_end))

            if bits:
                self.bits = build_bits(bits)


                    
            else:
                self.bits = []


            # add bits to Sample.html()
            try: 
                for item in self.bits:
                    self.html += '  [' + item.html + ']'
            except:
                pass


            
            try: 
                self.bits
                #print('self.bits: ', self.bits)
                #print('self.omm:', self.omm)
                for item in bits:
                    self.omm += '.' + item
                    #print('self.omm', self.omm)
            
            except:
                pass

            if self.omm[-1] == '.':
                self.omm = self.omm[:-1]
            
        
            imid = self.format(time_format=True, simple_text=True)
            split_items = imid.split("'")
            new_stri = split_items[0] + "'" + split_items[1]
            if self.title:
                new_stri += '.' + self.title.replace(" ","_")  # NB: Why hasn't this been done yet?
            if self.tags:
                for tag in self.tags:
                    new_stri += '.' + tag
            new_stri += "'" + split_items[2] 
            self.beta_format = new_stri

            self.beta_format_2 = self.format(time_format=False, simple_text=True)

    def __len__ (self):
        """Sample length in seconds."""

        self.length = self.time_end - self.time_start

        return(self.length)


    def methods(self):
        """Show methods and parameters."""

        result = []
        for item in dir(self):
            if item.startswith('__'):
                pass
            else:
                result.append(item)

        return(result)


    def __repr__(self):
        
        
        tag_string = "  ("                      # build tag string
        for i, tag in enumerate(self.tags):
            tag_string += str(tag)
            if (i + 1) < len(self.tags):
                tag_string += ', '
        tag_string += ')'
        
        result = self.title + tag_string + '  ' + str(self.time())

        if self.bits:
            result += '  ['
            for item in self.bits:
                result += item.title + ', '
        
            result = result[:-2] + ']'

        
        
        return(result)


    def __str__(self):
        
        return(self.omm)

    def play(self):
        """Open sample in tab in browser."""

        lib.Convert._browser_open(self.url)



    def update(self):
        """Updates sample 'url' and 'html' parameters."""
        
        self.url = 'https://www.youtube.com/embed/' + self.youtube_hash + '?start=' + str(self.time_start) + '&end=' + str(self.time_end) + '&rel=0' + '&autoplay=1'
        self.html = '<a title="' + " ".join(self.tags) + '" href="' + str(self.url) + '">' + str(self.title) + '</a>'

        # omm formatting
        self.omm = 'y.' + self.youtube_hash
        self.omm += '.' + self.youtube_time_format(self.time_start)
        
        if self.title: self.omm += '.' + self.title.replace(" ", "_")
        if self.tags:
            for tag in self.tags:
                self.omm += '.' + tag
            if self.omm[-1] == '.':
                    self.omm = self.omm[:-1]
        self.omm += '.' + str(self.youtube_time_format(self.time_end))

        if self.bits:
            for item in self.bits:
                self.omm += '.' + item.omm

        if self.omm[-1] == '.':
            self.omm = self.omm[:-1]


    def __add__(self, value):
        new_mixtape_obj = Mixtape(self, value)

        return(new_mixtape_obj)

    def __getitem__(self, value):
        if isinstance(value, int):
            if value >= 0:
                if value < len(self):
                    new_sample = copy.deepcopy(self)
                    new_sample.time_start = new_sample.time_start + value
                    new_sample.update()
                    #newSample = omm(new_sample.omm)
                    newSample = new_sample
                    return(newSample)
                else:
                    raise ValueError('Out of range')


    def __sub__(self, small_sample):
        """split first Sample with second Sample, 
        returns a tuple of two Samples,
        first Sample up to second Sample start and 
        first Sample from second Sample end onwards."""

        # test time range fit
        def test_sample_sub_time_range(full_sample, small_sample):
            if full_sample.youtube_hash != small_sample.youtube_hash:
                raise ValueError('different videos cannot be subtracted')
            else:
                if full_sample.time_start > small_sample.time_start:
                    raise ValueError('second sample time_start exceeds first sample time_start')
                else:
                    if full_sample.time_end < small_sample.time_end:
                        raise ValueError('second sample time_end exceeds first sample time_end')
                    else:
                        return(True)
    
        time_ranges_okay = test_sample_sub_time_range(self, small_sample)
        if time_ranges_okay:
            full_copy_1 = copy.deepcopy(self)
            full_copy_2 = copy.deepcopy(self)
            full_copy_1.time_end = small_sample.time_start
            full_copy_2.time_start = small_sample.time_end
            full_copy_1.update()
            full_copy_2.update()
            return(full_copy_1, full_copy_2)
        else:
            raise ValueError('subtraction not supported for these Samples')


    def time(self):
        """Show sample length in 1h2m3s format."""

        own_length_in_seconds = len(self)

        if own_length_in_seconds > 3599:
            hours = int(own_length_in_seconds / 3600)
            own_length_in_seconds = (own_length_in_seconds - (hours * 3600))
        else:
            hours = 0

        if own_length_in_seconds > 59:
            minutes = int(own_length_in_seconds / 60)
            own_length_in_seconds = (own_length_in_seconds - (minutes * 60))
        else:
            minutes = 0

        seconds = own_length_in_seconds
        time_string = ""

        if hours:
            time_string += str(hours) + "h"
        if minutes:
            time_string += str(minutes) + "m"
        if seconds:
            time_string += str(seconds) + "s"

        return(time_string)


    def youtube_time_format(self, seconds):
        """Takes time in seconds, returns YouTube format time code."""

        hours = int(seconds / 3600)
        seconds = seconds - (hours * 3600)
        minutes = int(seconds / 60)
        rest = seconds - minutes * 60
        final_str = ''
        if hours:
            final_str += str(hours) + 'h'
        if minutes:
            final_str += str(minutes) + 'm'
        if seconds:
            final_str += str(rest) + 's'

        return(final_str)
    

    def iframe(self, width=360, pause=False, title=False, center=True):
        """Returns IFrame format."""

        return(iframe(self, width=width, pause=pause, title=title, center=center))


    def format(self, format='h1', center=True, simple_text=False,bold=False, time_format=True, bold_time = False, dot_time_sep=False):
        """Returns HTML formatted Sample representation."""

        def boldness(input_str):
            """Add <b> tags to string (internal method)."""

            new_str = '<b>' + input_str + '</b>'
            return(new_str)

        yota_obj = self
        translate = yota_obj.youtube_time_format
        if time_format:
            myTuple = yota_obj.youtube_hash, translate(yota_obj.time_start), translate(yota_obj.time_end)
        else:
            myTuple = yota_obj.youtube_hash, str(yota_obj.time_start), str(yota_obj.time_end)
        res = ""
        for item in myTuple:
            res += str(item) + "'"
        res = res[:-1] 
        if bold:
            res_str = '<' + format + '>y.' + myTuple[0] + boldness("'" + myTuple[1] + "'" + myTuple[2]) + '</' + format + '>'
        elif bold_time:
            res_str = '<' + format + '>y.' + myTuple[0] + boldness("'") + '</b>' + myTuple[1] + boldness("'") + '</b>' + myTuple[2] + '</b>' + '</' + format + '>'  
        else:
            res_str = '<' + format + '>y.' + myTuple[0] + "'" + myTuple[1] + "'" + myTuple[2] + '</' + format + '>'
        if center:
            res_str = '<center>' + res_str + '</center>'
        if simple_text:
            res_str = ("y." + res) 
        if dot_time_sep:
            res_str = res_str.replace("'",".")
        return(res_str)      


    def vlc(self, full_screen=False):

        lib.Convert.vlc_open(self, full_screen=full_screen)


    def pad(self, shift_value):
        """Extends the Sample in time, positive integers extends the front and 
        negative integers extends the end."""

        # pad beginning
        if shift_value >= 0:
            sampleCopy = copy.deepcopy(self)
            sampleCopy.time_start = sampleCopy.time_start - shift_value  # pad with 5
            sampleCopy.update()
        # pad ending
        if shift_value < 0:
            sampleCopy = copy.deepcopy(self)
            sampleCopy.time_end = sampleCopy.time_end - shift_value  # is a negative no.
            sampleCopy.update()
        return(sampleCopy)


    def hash(self):
        m = hashlib.sha256()
        m.update(self.omm.encode())
        temp_hash = m.hexdigest()
        for i, char in enumerate(temp_hash):
            if char in string.ascii_letters:
                calculated_hash = temp_hash[i:i+11]
                return(calculated_hash)

        

class Cue():

    def __init__(self, yt_hash, title=None, time_start=0, tags=[], bits=[]):

        self.youtube_hash = yt_hash

        self.first_name = self.youtube_hash[:3]
        self.middle_name  =  self.youtube_hash[3:7]
        self.last_name = self.youtube_hash[7:]

        self.yt_time = time_start
        self.time_start = lib.Convert._time_str(time_start)
        self.tags = tags

        self.url = 'https://www.youtube.com/embed/' + self.youtube_hash + '?start=' + str(self.time_start) + '&rel=0' + '&autoplay=1'

        if title:
            title2 = title.replace("_", " ")
            self.title = title2
            if self.tags:
                if self.tags[0] == title:
                    self.tags.pop(0)

        else:
            self.title = None


        self.html = build_html(self)
        #self.html = '<a href="' + str(self.url) + '" title="' + " ".join(tags) +  '">' + str(self.title) + '</a>'


        # if tags:
        #     link_tags_read = []
        #     for item in self.tags:
        #         m = re._search('http', item)
        #         if m:
        #             link_tags_read.append(item)

        #     self.links = link_tags_read


        # omm formatting
        self.omm = 'y.' + self.youtube_hash
        self.omm += '.' + self.youtube_time_format(self.time_start)

        if self.title: self.omm += '.' + self.title.replace(" ", "_")
        if self.tags:
            for tag in self.tags:
                self.omm += '.' + tag

            if self.omm[-1] == '.':
                self.omm = self.omm[:-1]


        if bits:
            #print('bits:', str(bits))
            self.bits = []
            if len(bits) > 1:
                for item in bits:
                    bit_object = bno.main(item)
                    try:
                        bit_object.title 
                    except ValueError:
                        bit_object.title = 'myBit'
                        bit_object.update()
                    self.bits.append(bit_object)
            elif len(bits) == 1:
                bit_object = bno.main(bits[0])
                self.bits.append(bit_object)

                    
        else:
            self.bits = []


            
        try: 
            self.bits
            #print('self.bits: ', self.bits)
            #print('self.omm:', self.omm)
            for item in bits:
                self.omm += '.' + item
                #print('self.omm', self.omm)
        
        except:
            pass

        if self.omm[-1] == '.':
            self.omm = self.omm[:-1]


                # add bits to Yota.html()
        try: 
            for item in self.bits:
                
                self.html += '  [' + item.html + ']'
        except:
            pass



    def play(self):
        """Open sample in tab in browser."""

        lib.Convert._browser_open(self.url)


    def vlc(self, full_screen=False):

        lib.Convert.vlc_open(self, full_screen=full_screen)



    def __repr__(self):

        tag_string = "  ("                      # build tag string
        for i, tag in enumerate(self.tags):
            tag_string += str(tag)
            if (i + 1) < len(self.tags):
                tag_string += ', '
        tag_string += ')'

        result = ""
        if self.title:
            result = self.title + result

        if self.tags:
            tag_string = "  ("                      # build tag string
            for i, tag in enumerate(self.tags):
                tag_string += str(tag)
                if (i + 1) < len(self.tags):
                    tag_string += ', '
            tag_string += ')'
            result += tag_string

        if self.bits:
            result += '  ['
            for item in self.bits:
                result += item.title + ', '

            result = result[:-2] + ']'

        
        
        return(result)

        return(result)



    def __str__(self):
        
        return(self.omm)


    def __add__(self, value):

        new_mixtape_obj = Mixtape(self)
        new_mixtape_obj += value

        return(new_mixtape_obj)


    def youtube_time_format(self, seconds):
        """Takes time in seconds, returns YouTube format time code."""

        hours = int(seconds / 3600)
        seconds = seconds - (hours * 3600)
        minutes = int(seconds / 60)
        rest = seconds - minutes * 60
        final_str = ''
        if hours:
            final_str += str(hours) + 'h'
        if minutes:
            final_str += str(minutes) + 'm'
        if seconds:
            final_str += str(rest) + 's'

        return(final_str)

    def iframe(self, width=360, pause=False, title=False, center=True):
        """Returns IFrame format."""

        return(iframe(self, width=width, pause=pause, title=title, center=center))


    def update(self):
        """Updates sample 'url' and 'html' parameters."""

        self.url = 'https://www.youtube.com/embed/' + self.youtube_hash + '?start=' + str(self.time_start) + '&rel=0' + '&autoplay=1'

        # omm formatting
        self.omm = 'y.' + self.youtube_hash + '.' + str(self.youtube_time_format(self.time_start))
        
        if self.title: self.omm += '.' + self.title.replace(" ", "_")
        if self.tags:
            for tag in self.tags:
                self.omm += '.' + tag
            
            if self.omm[-1] == '.':
                self.omm = self.omm[:-1]

        if self.bits:
            for item in self.bits:
                self.omm += '.' + item.omm

        if self.omm[-1] == '.':
            self.omm = self.omm[:-1]



    def shift(self, shift_value):
        """Shift the Cue start time, positive integers moves start time forward and 
        negative integers moves it back."""

        # move start time forward
        if shift_value >= 0:
            CueCopy = copy.deepcopy(self)
            CueCopy.time_start = CueCopy.time_start + shift_value
            CueCopy.update()
        # move start time back
        if shift_value <= 0:
            if (shift_value * -1) < self.time_start: # check shift_value not exceeding Sample range
                CueCopy = copy.deepcopy(self)
                CueCopy.time_start = CueCopy.time_start + shift_value  # is a negative no.
                CueCopy.update()
            else:
                raise ValueError('Out of range')
        return(CueCopy)


    def to_sample(self, omm, add=0, time_end_str=None):
    
        cue_copy = copy.deepcopy(self)
        
        if add:
            new_omm = cue_copy.omm + '.' + str(cue_copy.time_start + add) + 's'
            new_sample = omm(new_omm)
            return(new_sample)

        elif time_end_str: 
            new_omm = cue_copy.omm + '.' + time_end_str
            new_sample = omm(new_omm)
            return(new_sample)
        

    def hash(self):
        m = hashlib.sha256()
        m.update(self.omm.encode())
        temp_hash = m.hexdigest()
        for i, char in enumerate(temp_hash):
            if char in string.ascii_letters:
                calculated_hash = temp_hash[i:i+11]
                return(calculated_hash)


    def methods(self):
        """Show methods and parameters."""

        result = []
        for item in dir(Yota):
            if item.startswith('__'):
                pass
            else:
                result.append(item)

        return(result)



class Yota():

    def __init__(self, yt_hash, tags=[], title=None, bits=[]):

        self.youtube_hash = yt_hash

        self.first_name = self.youtube_hash[:3]
        self.middle_name  =  self.youtube_hash[3:7]
        self.last_name = self.youtube_hash[7:]
        if tags:
            self.tags = tags
        else:
            self.tags = None

        if title:
            title2 = title.replace("_", " ")
            self.title = title2
            if self.tags:
                if self.tags[0] == title:
                    self.tags.pop(0)

        else:
            self.title = None


        self.url = 'https://www.youtube.com/embed/' + self.youtube_hash + '?start=0' + '&rel=0' + '&autoplay=1'
  
        if self.tags and self.title:
            self.html = '<a href="' + str(self.url) + '" title="' + " ".join(tags) +  '">' + str(self.title) + '</a>'
  
        elif self.title:
            self.html = '<a href="' + str(self.url) + '">' + str(self.title) + '</a>'

        else:
            self.html = '<a href="' + str(self.url) + '" title="' + str(self.tags) + '"> MyYota</a>'


        if bits:
            self.bits = []
            if len(bits) > 1:
                for item in bits:
                    bit_object = bno.main(item)
                    try:
                        bit_object.title 
                    except ValueError:
                        bit_object.title = 'myBit'
                        bit_object.update()
                    self.bits.append(bit_object)
            elif len(bits) == 1:
                bit_object = bno.main(bits[0])
                self.bits.append(bit_object)
                
        else:
            self.bits = []

        # add bits to Yota.html()
        try: 
            for item in self.bits:
                
                self.html += '  [' + item.html + ']'
        except:
            pass


        # omm formatting
        self.omm = 'y.' + self.youtube_hash

        if self.title: self.omm += '.' + self.title.replace(" ", "_")
        if self.tags:
            for tag in self.tags:
                self.omm += '.' + tag

        try: 
            self.bits
            #print('self.bits: ', self.bits)
            #print('self.omm:', self.omm)
            for item in bits:
                self.omm += '.' + item
                #print('self.omm', self.omm)
            
        except:
            pass

        if self.omm[-1] == '.':
            self.omm = self.omm[:-1]
            #self.update()


    def play(self):
        """Open sample in tab in browser."""

        lib.Convert._browser_open(self.url)


    def vlc(self, full_screen=False):
        """Play Yota in VLC Player."""

        lib.Convert.vlc_open(self, full_screen=full_screen)


    def methods(self):
        """Show methods and parameters."""

        result = []
        for item in dir(Yota):
            if item.startswith('__'):
                pass
            else:
                result.append(item)

        return(result)


    def __repr__(self):
        """Defines internal print() format (internal method)."""

        tag_string = "  ("                      # build tag string
        if self.tags:
            for i, tag in enumerate(self.tags):
                tag_string += str(tag)
                if (i + 1) < len(self.tags):
                    tag_string += ', '

        tag_string += ')'

        result = ""
        if self.title:
            result = self.title + result

        if self.tags:
            tag_string = "  ("                      # build tag string
            for i, tag in enumerate(self.tags):
                tag_string += str(tag)
                if (i + 1) < len(self.tags):
                    tag_string += ', '
            tag_string += ')'
            result += tag_string

        if self.bits:
            result += '  ['
            for item in self.bits:
                result += item.title + ', '

            result = result[:-2] + ']'

        
        
        return(result)

        return(result)


    def __str__(self):
        """Returns omm format string (internal method)."""

        return(self.omm)


    def __add__(self, value):

        new_mixtape_obj = Mixtape(self)
        new_mixtape_obj += value

        return(new_mixtape_obj)


    def iframe(self, width=360, pause=False, title=False, center=True):
        """Returns IFrame format."""

        return(iframe(self, width=width, pause=pause, title=title, center=center))


    def update(self):
        """Updates sample 'url' and 'html' parameters."""

        self.url = 'https://www.youtube.com/embed/' + self.youtube_hash + '?start=0' + '&rel=0' + '&autoplay=1'
  
        # omm formatting
        self.omm = 'y.' + self.youtube_hash
          
        if self.title: self.omm += '.' + self.title.replace(" ", "_")
        if self.tags:
            for tag in self.tags:
                self.omm += '.' + tag

        if self.bits:
            for item in self.bits:
                self.omm += '.' + item.omm

        if self.omm[-1] == '.':
            self.omm = self.omm[:-1]
        
    
    def to_sample(self, add=0, time_end_str=None, time_start_str=False):
    
        yota_copy = copy.deepcopy(self)
        
        if time_start_str:
            start_time = time_start_str
        else:
            start_time = '1s'

        if add:
            new_omm = yota_copy.omm + '.' + start_time + '.' + str(time_start + add) + 's'   # NB: 0s bug to be fixed
            new_sample = omm(new_omm)
            return(new_sample)

        elif time_end_str: 
            new_omm = yota_copy.omm + '.' + start_time + '.' + time_end_str
            new_sample = omm(new_omm)
            return(new_sample)


    def srt_search(self, keyword, clip_length=10):

        myMixtape = srt.srt_search(self, lib.Convert.omm, Mixtape, keyword, clip_length)

        return(myMixtape)


    def hash(self):
        m = hashlib.sha256()
        m.update(self.omm.encode())
        temp_hash = m.hexdigest()
        for i, char in enumerate(temp_hash):
            if char in string.ascii_letters:
                calculated_hash = temp_hash[i:i+11]
                return(calculated_hash)