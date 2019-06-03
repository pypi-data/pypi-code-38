import re, json, requests
from more_itertools import unique_everseen
from . import yn, sh, yno, bno
from . import yota
from . import omm_file_parser
from . import online_omm_parser
from . import cnf
from . import ono
from . import onoObject


class Convert():

    def readme():
        """Returns README.md Markdown file content."""

        file_path = cnf.package_path + cnf.os_sep + 'README.md'
        with open(file_path, 'r') as f:
            file_content = f.read()
            
            return file_content


    def search(search_term, exclusive_terms=[], mixtape=False):
        """Search omm() parsing history,
        return list of result strings, 
        optionally Mixtape."""

        # create a MediabyteHashObj (with current parsing history)
        o = onoObject.MediabyteHashObj()
        result = []
        for item in o: 
            if search_term in o[item] or search_term in item:
                exclusive_match = False
                if exclusive_terms:

                    for exclusive_term in exclusive_terms:
                        #print(f'o[item]: {o[item]}, ex_term: {exclusive_term}')
                        m = re.search(exclusive_term, o[item])
                        if m:
                            exclusive_match = True
                # break loop cycle if exclusive match
                if exclusive_match == True:
                    #print(f'dropping {o[item]}')
                    continue

                result.append(o[item])
                if mixtape:
                    # append to Mixtape
                    try:
                        myMix += Convert.omm(o[item])
                    # create new Mixtape
                    except:
                        myMix = yota.Mixtape(Convert.omm(o[item]))

        if mixtape:
            return myMix
        else:
            return result


    def sync():
        """Upload local hash_dict to server."""
        filename = cnf.hash_dict_path
        with open(filename, 'r') as f:
            hash_dict = json.load(f)

        resp = requests.post('http://taext.pythonanywhere.com/post', json=hash_dict)
        if resp:
            print(resp.content.decode())
        else:
            print(resp)


    def filter(omm_str, contains=[], does_not_contain=[]):
        """Takes omm string, contains and does_not_contain lists, returns Bool"""
        
        def test_for_tag(tag, omm_str):
            """Test for tag in omm string"""
            m = re.search('[\.^]' + tag + '(\.|$)', omm_str)
            if m: return(True)
            else: return(False)
        
        # OR filtering       (using contains list)
        for item in contains:
            contains_tag_check = test_for_tag(item, omm_str)            
            if contains_tag_check:
                # NOT filtering      (using does_not_contain list)
                for item in does_not_contain:
                    tag_exclusion_check = test_for_tag(item, omm_str)
                    if tag_exclusion_check:
                        return False
                # return OR filtering result
                return contains_tag_check                


    def youtube_takeout_to_omm(youtube_takeout_html_filename, omm_filename):
        """Takes local YouTube watch history HTML filename, writes .omm Mixtape file."""
        
        with open(youtube_takeout_html_filename,'r') as f:
            file_content = f.read()
        m = re.findall('videoId\":"(\S{11})\"', file_content)
        non_results = list(unique_everseen(m))
        m2 = re.findall('v=([a-zA-Z0-9\_\-]{11})', file_content)
        results2 = list(unique_everseen(m2))
        
        with open(omm_filename,'w') as f:
            for item in results2:
                # NB: Hacky, filtering y.y results (because of faulty .y. mixtape splitting)
                #m = re.search('^y', item)
                #if not m:
                f.write('y.' + item)
                f.write('\n')


    def youtube_html_to_omm(youtube_html_filename, omm_filename):
        """Takes saved YouTube playlist HTML filename, writes .omm mixtape file."""
        
        with open(youtube_html_filename,'r') as f:
            file_content = f.read()
        m = re.findall('videoId\":"(\S{11})\"', file_content)
        non_results = list(unique_everseen(m))
        m2 = re.findall('v=([a-zA-Z0-9\_\-]{11})', file_content)
        results2 = list(unique_everseen(m2))
        
        with open(omm_filename,'w') as f:
            for item in results2[21:]:
                # NB: Hacky, filtering y.y results (because of faulty .y. mixtape splitting)
                m = re.search('^y', item)
                if not m:
                    f.write('y.' + item)
                    f.write('\n')


    def docs():
        """Open online documentation in browser."""
        sh.ell('google-chrome','https://github.com/taext/mediabyte/tree/master/user_guide')


    def _time_str(time_str):
        """Takes '2h5m3s' format time string, returns value in seconds (internal method)."""

        m = re.search('([0-9]+)s', time_str)   # match seconds
        m2 = re.search('([0-9]+)m', time_str)  # match minutes
        m3 = re.search('([0-9]+)h', time_str)  # match hours

        if m:
            seconds = m.group(1)
        else: seconds = 0

        if m2:
            minutes = m2.group(1)
        else: minutes = 0

        if m3:
            hours = m3.group(1)
        else: hours = 0

        seconds_total = int(seconds) + (int(minutes) * 60) + (int(hours) * 3600)

        return(seconds_total)


    # def code_length():
    #     """Show total code line count."""

    #     f = open('mediabyte.py','r')
    #     lines = f.readlines()

    #     lines_of_code = []
    #     for line in lines:

    #         if len(line) > 5:
    #             m = re.search('^\s*#', line)    # check for comment line to be excluded
    #             m2 = re.search('\"\"\"', line)  # check for docstrings to be excluded
    #             if m or m2:
    #                 pass
    #             else:
    #                 lines_of_code.append(line)

    #     return(len(lines_of_code))


    def version():
        """Show version number."""
        # get version from cnf.py
        version_string = cnf.version_number

        return(version_string)


    def methods():
        """Show methods and parameters."""

        result = []
        for item in dir(Convert):
            if item.startswith('__'):
                pass
            else:
                result.append(item)

        return(result)


    def _browser_open(*input_url):
        """Open URL in Chrome tab (internal method)."""

        sh.ell('google-chrome', *input_url)


    # def whats_new():
    #     """Show What's New comment"""

    #     resource_package = 'mediabyte'  # Could be any module/package name
    #     resource_path = '/'.join(('files', 'parse.py'))  # Do not use os.path.join()
    #     file_lines = str(pkg_resources.resource_string(resource_package, resource_path)).split("\n")
    
    #     for item in file_lines[:100]:
    #         m = re.search('Whats New: (.*?)\\n', item)
    #         if m:
    #             return m.group(1)


    def _determine_type(item):
        """Takes yno string, returns yota object type."""

        res = yno.main(item)
        time_code_list = res[0] # get time code occurrences
        m = re.findall('\.y\.', item) # test for Mixtape
        if m: 
            if len(m) >= 1:  # '.y.' match means Mixtape
                answer = 'Mixtape'
        # if no Mixtape match
        elif len(time_code_list) == 1: # 1 time code means Cue
            answer = 'Cue'
        elif len(time_code_list) == 2: # 2 time cods means Sample
            answer = 'Sample'
        elif len(time_code_list) == 0: # 0 time code means Yota
            answer = 'Yota'
        else:
            raise ValueError('unknown format')
            answer = None
        return(answer)


    def vlc_open(self, full_screen=False):
            """Play Sample in VLC player (internal method)."""
            
            obj_type = Convert._determine_type(self.omm)

            url = self.url
            if obj_type == 'Sample':
                start_time = '--start-time=' + str(self.time_start)
                stop_time = '--stop-time=' + str(self.time_end)
                if full_screen:
                    sh.ell('vlc', url, start_time, stop_time, '--fullscreen')
                else:                    
                    sh.ell('vlc',url, start_time, stop_time)
            
            if obj_type == 'Cue':
                start_time = '--start-time=' + str(self.time_start)
                sh.ell('vlc',url, start_time)

            if obj_type == 'Yota':
                sh.ell('vlc',url)


    # def url_file_to_mixtape(filename):
    
    #     with open(filename) as f:
    #         urls = f.readlines()

    #     # remove newlines
    #     urls2 = []
    #     for item in urls:
    #         urls2.append(item.rstrip())
    #     # start mixtape with first url    
    #     if len(urls2) > 0:
    #         mixtape = Convert.omm(urls2[0])
    #     # build mixtape with remaining urls    
    #     if len(urls2) > 1:
    #         for item in urls2[1:]:
    #             mixtape += Convert.omm(item)
                
    #     return mixtape


    def url_list_to_mixtape(url_list):
    
        urls = url_list
        # remove newlines
        urls2 = []
        for item in urls:
            urls2.append(item.rstrip())
        # start mixtape with first url    
        if len(urls2) > 0:
            mixtape = Convert.omm(urls2[0])
        # build mixtape with remaining urls    
        if len(urls2) > 1:
            for item in urls2[1:]:
                mixtape += Convert.omm(item)
                
        return mixtape


    def search_to_mixtape(search_string, clip_length=0, time_end_str="", time_start_str=""):
        """Takes yn format YouTube string, returns Mixtape of Yotas, 
        optional clip_length argument returns Mixtape of Samples."""
    
        urls = yn.return_results(search_string)
        myMix = Convert.url_list_to_mixtape(urls)

        for i, item in enumerate(myMix):
            item.title = search_string.capitalize() + ' - ' + str(i+1)
            item.update()

        if clip_length:
            first_sample = myMix[0].to_sample(add=clip_length)
            new_mix = yota.Mixtape(first_sample)
            for item in myMix[1:]:
                new_sample = item.to_sample(add=clip_length)
                new_mix += new_sample
            myMix = new_mix

        elif time_end_str:

            if not time_start_str:
                time_start_str = '1s'

            first_sample = myMix[0].to_sample(time_end_str=time_end_str, time_start_str=time_start_str)
            new_mix = yota.Mixtape(first_sample)
            for item in myMix[1:]:
                new_sample = item.to_sample(time_end_str=time_end_str, time_start_str=time_start_str)
                new_mix += new_sample
            myMix = new_mix

        return myMix


    def search_to_mixtape_player(search_string, filename, clip_length=False, time_end_str=False):
        """Takes yn format YouTube string and filename,
        writes Mixtape player HTML file."""

        mix_obj = Convert.search_to_mixtape(search_string, clip_length, time_end_str=time_end_str)

        mix_obj.write_player_html(filename)


    def omm(omm_str, remember=True):
        """Takes OMM format string, returns MediaByte object."""
        
        def parse_omm_mixtape(inp):
            """Split mixtape string into list (split on .y)."""

            newInp = inp.split('.y.')
            omm_lines = [newInp[0]]
            for item in newInp[1:]:
                omm_lines.append("y." + item)
            return(omm_lines)


        def build_omm_mixtape(mix_list):
            """Takes yno string list from parse_omm_mixtape(), returns Mixtape object."""

            myMixtape = yota.Mixtape(parse_object(mix_list[0]))
            for item in mix_list[1:]:
                yotaObject = parse_object(item)
                myMixtape += yotaObject
            return(myMixtape)


        def parse_object(in_obj):
            """Takes yno string, returns yota object: Sample, Cue, Yota or Mixtape."""
            
            # test for bit
            m = re.search('^b\.', in_obj)
            if m:
                myBit = bno.main(in_obj)
                return(myBit)

            type_result = determine_type(in_obj)
            parsing_res = yno.main(in_obj)

            if len(parsing_res[1]) > 0:
                title = parsing_res[1][0]
            else:
                title = 'My' + type_result

            


            if type_result == 'Sample':
                # Sample hash bit object(s)
                if len(parsing_res[4]) > 0:
                    mySample = yota.Sample(url=parsing_res[2], time_start=Convert._time_str(parsing_res[0][0]), time_end=Convert._time_str(parsing_res[0][1]), title=title, tags=parsing_res[3], bits=parsing_res[4])
                else:
                    mySample = yota.Sample(url=parsing_res[2], time_start=Convert._time_str(parsing_res[0][0]), time_end=Convert._time_str(parsing_res[0][1]), title=title, tags=parsing_res[3])
                return(mySample)
            if type_result == 'Cue':
                # Cue has bit object(s)
                if len(parsing_res[4]) > 0:
                    myCue = yota.Cue(parsing_res[2], time_start=parsing_res[0][0], title=title, tags=parsing_res[3], bits=parsing_res[4])
                else:
                    myCue = yota.Cue(parsing_res[2], time_start=parsing_res[0][0], title=title, tags=parsing_res[3])
                return(myCue)
            if type_result == 'Yota':
                # Yota has bit object(s)
                if len(parsing_res) == 5:
                    myYota = yota.Yota(parsing_res[2], title=title, tags=parsing_res[3], bits=parsing_res[4])
                else:
                    myYota = yota.Yota(parsing_res[2], title=title, tags=parsing_res[3])
                return(myYota)
            if type_result == 'Mixtape':
                mixtape_lines = parse_omm_mixtape(in_obj)
                myMixtape = build_omm_mixtape(mixtape_lines)
                return(myMixtape)


        def determine_type(item):
            """Takes yno string, returns yota object type."""

            res = yno.main(item)
            time_code_list = res[0] # get time code occurrences
            m = re.findall('\.y\.', item) # test for Mixtape
            m2 = re.search('^b\.', item)  # test for Bit.Link
            m3 = re.search('\.mp3\W', item) # test for Bit.Mp3
            # Bit matched
            if m2 and not m3:
                answer = 'bit.Link'
            elif m2:
                answer = 'bit.Mp3'
            elif m: 
                if len(m) >= 1:  # '.y.' match means Mixtape
                    answer = 'Mixtape'
            # if no Mixtape match
            elif len(time_code_list) == 1: # 1 time code means Cue
                answer = 'Cue'
            elif len(time_code_list) == 2: # 2 time cods means Sample
                answer = 'Sample'
            elif len(time_code_list) == 0: # 0 time code means Yota
                answer = 'Yota'
            else:
                raise ValueError('unknown format')
                answer = None
            return(answer)


        def check_for_full_youtube_url(url):

            """ parse YouTube URL and return Yota object string y.youtubehash."""
            
            # NB: Hacky, correct for updated share link format
            # https://youtu.be/UW_oi30h4vU?t=480 (no hms)
            m = re.search('youtu.be', url)
            m2 = re.search('t=\d+$', url)
            if m and m2:
                url += 's'

            m3 = re.search('time_continue=(\d+)', url)
            if m3:
                m4 = re.search('v=([a-zA-Z0-9\_\-]{11})', url)
                new_str = 'y.' + str(m4.group(1)) + '.' + m3.group(1) + 's'
                return(new_str)
            
            
            if url[-13:-11] == 'v=':
                new_str = 'y.' + url[-11:]
                return(new_str)
            # example: https://www.youtube.com/watch?v=eBVGYdHNUW4
            
            
            m = re.search('t=([\dsmh]+)$', url)
            m2 = re.search('([a-zA-Z0-9\_\-]{11})', url)
            if m:
                new_str = 'y.' + str(m2.group(1)) + '.' + str(m.group(1))
                return(new_str)
            
            

        def check_for_online_omm(input_str):
            # check for .omm input_str ending
            omm_check = re.search('\.omm$', input_str)
            # check for http input_str start
            http_check = re.search('^http', input_str)
            if omm_check and http_check:
                omm_object = online_omm_parser.main(input_str, Convert.omm)
                return(omm_object)


            
        
        def check_for_yota_file(input_str):
            """Takes omm string, checks for .omm ending"""

            m = re.search('\.omm$', input_str)
            if m:
                omm_object = omm_file_parser.main(input_str, Convert.omm)
                return(omm_object)


        def split_yotas(yotas_str):

            m = re.search('\.y\.', yotas_str)
            if m: # check not matching y.youtubehash (hash starting with y)
                my_list = yotas_str.split('.y.')
                new_list = [my_list[0]]
                for item in my_list[1:]:
                    new_str = 'y.' + item
                    new_list.append(new_str)
                return(new_list)
            else:
                return(yotas_str)

        def check_for_ono(input_str):
            # check for o.mediabytehash
            m = re.search('^o\.', input_str)
            if m:
                myObject = ono.check_ono(input_str)
                return(myObject)

        def check_for_bit_mixtape(input_str):
            starts_with_bit_check = re.search('^b\.', input_str)
            bit_mixtape_check = re.search('\.b\.', input_str)
            if starts_with_bit_check and bit_mixtape_check:
                return(True)
        
        def parse_bit_mixtape(input_str):
            my_list = input_str.split('.b.')
            new_list = [my_list[0]]
            for item in my_list[1:]:
                new_str = 'b.' + item
                new_list.append(new_str)
            myMix = bno.main(new_list[0]) + bno.main(new_list[1])
            for item in new_list[2:]:
                myMix += bno.main(item)
            return(myMix)


        # check for online .omm
        result = check_for_online_omm(omm_str)
        if result:
            return(result)


        # check for bit Mixtape
        result = check_for_bit_mixtape(omm_str)
        if result:
            bitMix = parse_bit_mixtape(omm_str)
            return(bitMix)

        # check for ono string (in hash_dict.json)
        result = check_for_ono(omm_str)
        if result is not None:
            return(result)
        # add to hash_dict if not recognized
        else:
            if remember == True:
                # check for b. or y. (to avoid non-mediabyte entries)
                m = re.search('^[by]\.', omm_str)
                if m:
                    ono.add_to_hash_dict(omm_str)


        # check for full YouTube URL, parse to Yota string 
        omm_str = omm_str.strip()
        result = check_for_full_youtube_url(omm_str)
        if result:
            omm_str = result
        # check for .yota file
        file_check = check_for_yota_file(omm_str)
        if file_check:
            omm_str = file_check

        # mixtape handling
        omm_lines = split_yotas(omm_str)
        if isinstance(omm_lines, list):
            myMix = parse_object(omm_lines[0])
            for line in omm_lines[1:]:
                myMix += parse_object(line)
            return(myMix)

        m = re.search('^[by]\.', omm_str)
        if m:
            return(parse_object(omm_str))
        else:
            raise ValueError("input doesn't compute")

