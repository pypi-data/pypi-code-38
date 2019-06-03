#!/home/dd/anaconda3/bin/python

import unittest, os
from files import lib
from files import bit
from files import yota_fuzz
from files import omm_file_parser


class Testomm(unittest.TestCase):

    def setUp(self):
        pass


### TAGS AND TITLE

    def test_sample_full(self):
        sample_test_str = 'y.8ZtHhF9Lt_8.1s.Welcome_&_Sponsors.podcast.intro.1m58s'
        result = lib.Convert.omm(sample_test_str)
        self.assertEqual(result.__repr__()[:7], 'Welcome')
        self.assertEqual(result.tags, ['podcast','intro'])
        self.assertEqual(result.time_start, 1)
        self.assertEqual(result.time_end, 118)
        self.assertEqual(result.time(), '1m57s')
        self.assertEqual(result.youtube_hash, '8ZtHhF9Lt_8')

    def test_cue_full(self):
        cue_test_str = 'y.8ZtHhF9Lt_8.1s.Welcome_&_Sponsors.podcast.intro'
        result = lib.Convert.omm(cue_test_str)
        self.assertEqual(result.__repr__()[:7], 'Welcome')
        self.assertEqual(result.tags, ['podcast','intro'])
        self.assertEqual(result.time_start, 1)
        self.assertEqual(result.youtube_hash, '8ZtHhF9Lt_8')

    def test_yota_full(self):
        cue_test_str = 'y.8ZtHhF9Lt_8.Welcome_&_Sponsors.podcast.intro'
        result = lib.Convert.omm(cue_test_str)
        self.assertEqual(result.__repr__()[:7], 'Welcome')
        self.assertEqual(result.tags, ['podcast','intro'])
        self.assertEqual(result.youtube_hash, '8ZtHhF9Lt_8')


#### NO TAGS
    
    def test_sample_no_tags(self):
        sample_test_str = omm_str = 'y.8ZtHhF9Lt_8.1s.Welcome_&_Sponsors.1m58s'
        result = lib.Convert.omm(sample_test_str)
        self.assertEqual(result.__repr__()[:7], 'Welcome')
        self.assertEqual(result.time_start, 1)
        self.assertEqual(result.time_end, 118)
        self.assertEqual(result.time(), '1m57s')
        self.assertEqual(result.youtube_hash, '8ZtHhF9Lt_8')

    def test_cue_no_tags(self):
        cue_test_str = 'y.8ZtHhF9Lt_8.1s.Welcome_&_Sponsors'
        result = lib.Convert.omm(cue_test_str)
        self.assertEqual(result.__repr__()[:7], 'Welcome')
        self.assertEqual(result.time_start, 1)
        self.assertEqual(result.youtube_hash, '8ZtHhF9Lt_8')

    def test_yota_no_tags(self):
        cue_test_str = 'y.8ZtHhF9Lt_8.Welcome_&_Sponsors'
        result = lib.Convert.omm(cue_test_str)
        self.assertEqual(result.__repr__()[:7], 'Welcome')
        self.assertEqual(result.youtube_hash, '8ZtHhF9Lt_8')


### NO TITLE

    def test_sample_no_title(self):
        sample_test_str = omm_str = 'y.8ZtHhF9Lt_8.1s.podcast.intro.1m58s'
        result = lib.Convert.omm(sample_test_str)
        self.assertEqual(result.__repr__()[:8], 'MySample')
        self.assertEqual(result.tags, ['podcast','intro'])
        self.assertEqual(result.time_start, 1)
        self.assertEqual(result.time_end, 118)
        self.assertEqual(result.time(), '1m57s')
        self.assertEqual(result.youtube_hash, '8ZtHhF9Lt_8')

    def test_cue_no_title(self):
        cue_test_str = 'y.8ZtHhF9Lt_8.1s.podcast.intro'
        result = lib.Convert.omm(cue_test_str)
        self.assertEqual(result.__repr__()[:5], 'MyCue')
        self.assertEqual(result.tags, ['podcast','intro'])
        self.assertEqual(result.youtube_hash, '8ZtHhF9Lt_8')

    def test_yota_no_title(self):
        cue_test_str = 'y.8ZtHhF9Lt_8.podcast.intro'
        result = lib.Convert.omm(cue_test_str)
        self.assertEqual(result.__repr__()[:6], 'MyYota')
        self.assertEqual(result.tags, ['podcast','intro'])
        self.assertEqual(result.youtube_hash, '8ZtHhF9Lt_8')


### NO TAGS & TITLE

    def test_sample_no_title_or_tags(self):
        sample_test_str = 'y.8ZtHhF9Lt_8.1s.1m58s'
        result = lib.Convert.omm(sample_test_str)
        self.assertEqual(result.__repr__()[:8], 'MySample')
        my_str_name = result.__str__()
        self.assertEqual(my_str_name[-5:], '1m58s')
        self.assertEqual(result.youtube_hash, '8ZtHhF9Lt_8')

    def test_cue_no_title_or_tags(self):
        sample_test_str = 'y.8ZtHhF9Lt_8.1m58s'
        result = lib.Convert.omm(sample_test_str)
        my_str_name = result.__str__()
        self.assertEqual(my_str_name[-11:], '1m58s.MyCue')
        self.assertEqual(result.time_start, 118)
        self.assertEqual(result.youtube_hash, '8ZtHhF9Lt_8')

    def test_yota_no_title_or_tags(self):
        sample_test_str = 'y.8ZtHhF9Lt_8'
        result = lib.Convert.omm(sample_test_str)
        my_str_name = result.__str__()
        self.assertEqual(my_str_name[-6:], 'MyYota')
        self.assertEqual(result.youtube_hash, '8ZtHhF9Lt_8')


### MIXTAPE

    def test_mixtape_full(self):
        
        mixtape_test_str = 'y.8ZtHhF9Lt_8.1s.Welcome_&_Sponsors.podcast.intro.1m58s.y.8ZtHhF9Lt_8.1m59s.Intro_banter.podcast.episode.overview.3m46s.y.8ZtHhF9Lt_8.3m47s.Overview.episode.overview.6m16s.y.8ZtHhF9Lt_8.6m17s.Sponsor:_ITPro_TV.sponsor.10m13s'
        mixtapeObj = lib.Convert.omm(mixtape_test_str)
        self.assertEqual(mixtapeObj.__repr__()[3:10], 'Welcome')
        self.assertEqual(len(mixtapeObj.content), 4)
        self.assertEqual(mixtapeObj[0].tags, ['podcast','intro'])
        self.assertEqual(mixtapeObj[0].time_end, 118)
        self.assertEqual(mixtapeObj[0].youtube_hash, '8ZtHhF9Lt_8')

    def test_mixtape_no_tags(self):
        
        mixtape_test_str = 'y.8ZtHhF9Lt_8.1s.Welcome_&_Sponsors.1m58s.y.8ZtHhF9Lt_8.1m59s.Intro_banter.podcast.episode.overview.3m46s.y.8ZtHhF9Lt_8.3m47s.Overview.episode.overview.6m16s.y.8ZtHhF9Lt_8.6m17s.Sponsor:_ITPro_TV.10m13s'
        mixtapeObj = lib.Convert.omm(mixtape_test_str)
        self.assertEqual(mixtapeObj.__repr__()[3:10], 'Welcome')
        self.assertEqual(len(mixtapeObj.content), 4)
        self.assertEqual(mixtapeObj[0].time_end, 118)
        self.assertEqual(mixtapeObj[0].youtube_hash, '8ZtHhF9Lt_8')

    def test_mixtape_no_title(self):
        
        mixtape_test_str = 'y.8ZtHhF9Lt_8.1s.podcast.intro.1m58s.y.8ZtHhF9Lt_8.1m59s.podcast.episode.overview.3m46s.y.8ZtHhF9Lt_8.3m47s.episode.overview.6m16s.y.8ZtHhF9Lt_8.6m17s.sponsor.10m13s'
        mixtapeObj = lib.Convert.omm(mixtape_test_str)
        self.assertEqual(mixtapeObj.__repr__()[3:11], 'MySample')
        self.assertEqual(len(mixtapeObj.content), 4)
        self.assertEqual(mixtapeObj[0].tags, ['podcast','intro'])
        self.assertEqual(mixtapeObj[0].time_end, 118)
        self.assertEqual(mixtapeObj[0].youtube_hash, '8ZtHhF9Lt_8')

    def test_mixtape_no_tags_or_title(self):
        
        mixtape_test_str = 'y.8ZtHhF9Lt_8.1s.1m58s.y.8ZtHhF9Lt_8.1m59s.3m46s.y.8ZtHhF9Lt_8.3m47s.6m16s.y.8ZtHhF9Lt_8.6m17s.10m13s'
        mixtapeObj = lib.Convert.omm(mixtape_test_str)
        self.assertEqual(mixtapeObj.__repr__()[3:11], 'MySample')
        self.assertEqual(len(mixtapeObj.content), 4)
        self.assertEqual(mixtapeObj[0].time_end, 118)
        self.assertEqual(mixtapeObj[0].youtube_hash, '8ZtHhF9Lt_8')

    def test_mixtape_no_tags_or_title_or_time_codes(self):
        
        mixtape_test_str = 'y.8ZtHhF9Lt_8.y.8ZtHhF9Lt_8.y.8ZtHhF9Lt_8.3m47s.6m16s.y.8ZtHhF9Lt_8.6m17s.10m13s'
        mixtapeObj = lib.Convert.omm(mixtape_test_str)
        self.assertEqual(mixtapeObj.__repr__()[3:9], 'MyYota')
        self.assertEqual(len(mixtapeObj.content), 4)
        self.assertEqual(mixtapeObj[0].youtube_hash, '8ZtHhF9Lt_8')

    def test_mixtape_oneline_format(self):
        mixtape_test_str = 'y.drRQVI58c-E.1m18s.Koreans_on_Metoo.interview.asia.2m0s.y.drRQVI58c-E.1m18s.Koreans_on_Metoo.interview.asia.2m0s'
        mixtapeObj = lib.Convert.omm(mixtape_test_str)
        self.assertEqual(mixtapeObj.omm_oneline(), 'y.drRQVI58c-E.1m18s.Koreans_on_Metoo.interview.asia.2m0s.y.drRQVI58c-E.1m18s.Koreans_on_Metoo.interview.asia.2m0s')


## YOUTUBE URL PARSING
    
    # no time code, only YouTube hash
    # def test_youtube_url_parsing_0(self): 
    #     youtube_url_fourth_format = 'NI1L8ZJgA9o'
    #     yota_object = lib.Convert.omm(youtube_url_fourth_format)
    #     self.assertEqual(yota_object.omm, 'y.NI1L8ZJgA9o.MyYota')

    # no time code, basic YouTube URL
    def test_youtube_url_parsing(self): 
        youtube_url_first_format = 'https://www.youtube.com/watch?v=NI1L8ZJgA9o'
        yota_object = lib.Convert.omm(youtube_url_first_format)
        self.assertEqual(yota_object.omm, 'y.NI1L8ZJgA9o.MyYota')

    # with time code, from YouTube share link with time code (old format)
    def test_youtube_url_parsing_2(self):
        youtube_url_second_format = 'https://youtu.be/NI1L8ZJgA9o?t=60s'
        cue_object = lib.Convert.omm(youtube_url_second_format)
        self.assertEqual(cue_object.omm, 'y.NI1L8ZJgA9o.1m0s.MyCue')

    # with time code, from YouTube share link with time code (new format)
    def test_youtube_url_parsing_4(self):
        youtube_url_second_format = 'https://youtu.be/NI1L8ZJgA9o?t=120'
        cue_object = lib.Convert.omm(youtube_url_second_format)
        self.assertEqual(cue_object.omm, 'y.NI1L8ZJgA9o.2m0s.MyCue')

    # with time code, from clicking YouTube logo when in embedded player
    def test_youtube_url_parsing_3(self):
        youtube_url_third_format = 'https://www.youtube.com/watch?time_continue=60&v=drRQVI58c-E'
        cue_object = lib.Convert.omm(youtube_url_third_format)
        self.assertEqual(cue_object.omm, 'y.drRQVI58c-E.1m0s.MyCue')


## JAVASCRIPT HTML PLAYER Mixtape.player() 

    def test_mixtape_player(self):
        test_mix_object = lib.Convert.omm('y.drRQVI58c-E.1m18s.Koreans_on_Metoo.interview.asia.2m0s.y.drRQVI58c-E.1m18s.Koreans_on_Metoo.interview.asia.2m0s')
        obj_jule = test_mix_object.player()
        test_jule = '<iframe width="360" height="216" title="Koreans on Metoo" src="https://www.youtube.com/embed/drRQVI58c-E?start=78&end=120&rel=0&autoplay=0&enablejsapi=1" frameborder=0 allowfullscreen></iframe> <iframe width="360" height="216" title="Koreans on Metoo" src="https://www.youtube.com/embed/drRQVI58c-E?start=78&end=120&rel=0&autoplay=0&enablejsapi=1" frameborder=0 allowfullscreen></iframe> <!DOCTYPE html>\n                                <html lang="en">\n                                <head>\n                                <meta charset="utf-8">\n                                <meta name="viewport" content="width=device-width, initial-scale=1">\n                                <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">\n                                <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.0/jquery.min.js"></script>\n                                <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js"></script>\n                                <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>\n                                <title> YouTube Koreans on Met</title>\n                                </head>\n                                <body>\n\n                                <script src="https://www.youtube.com/iframe_api"></script><script>function onYouTubeIframeAPIReady() { window.yotasamples = {}; let i = 0;  for (let ifrm of document.getElementsByTagName("iframe")) {       ifrm.id = "sample" + i;      ifrm.yotaidx = i;      window.yotasamples[i] = new YT.Player(ifrm.id, {events: {"onStateChange": playerStateChange}});        i++;  }}  function playerStateChange(event) {    console.log(event.data);    switch(event.data) {        case 0:            let myidx = event.target.getIframe().yotaidx;            event.target.getIframe().classList.remove("current");if (window.yotasamples[myidx+1]) { window.yotasamples[myidx+1].getIframe().classList.add("current");window.yotasamples[myidx+1].playVideo();} else{window.yotasamples[0].getIframe().classList.add("current")}                        break    }  }document.querySelector("iframe").classList.add("current");</script><input type=button style="position:fixed;bottom:0;left:0" value="Toggle View" onclick="document.documentElement.classList.toggle(this.dataset.targetclass);" data-targetclass=julekalenderview><style>html:not(.julekalenderview) iframe:not(.current) {display:none} </style>\n\n                                </body>\n                                </html>\n\n'
        self.assertEqual(obj_jule[:1000], test_jule[:1000])


## IFRAME METHODS

    def test_cue_iframe(self):
        test_cue_object = lib.Convert.omm('y.gCLoXNL-AAI.1s.Rocket Beans Live')  # live stream, does it matter?
        test_iframe = '<center><iframe width="360" height="216" title="Rocket Beans Live" src="https://www.youtube.com/embed/gCLoXNL-AAI?start=1&rel=0&autoplay=1" frameborder=0 allowfullscreen></iframe></center>'
        self.assertEqual(test_cue_object.iframe(), test_iframe)

    def test_yota_iframe(self):
        test_cue_object = lib.Convert.omm('y.gCLoXNL-AAI.Rocket Beans Live')  # live stream, does it matter?
        test_iframe = '<center><iframe width="360" height="216" title="Rocket Beans Live" src="https://www.youtube.com/embed/gCLoXNL-AAI?start=0&rel=0&autoplay=1" frameborder=0 allowfullscreen></iframe></center>'
        self.assertEqual(test_cue_object.iframe(), test_iframe)

    def test_sample_iframe(self):
        test_cue_object = lib.Convert.omm('y.drRQVI58c-E.1s.Rocket Beans Live.4s')  # live stream, does it matter?
        test_iframe = '<center><iframe width="360" height="216" title="Rocket Beans Live" src="https://www.youtube.com/embed/drRQVI58c-E?start=1&end=4&rel=0&autoplay=1" frameborder=0 allowfullscreen></iframe></center>'
        self.assertEqual(test_cue_object.iframe(), test_iframe)


# MANUAL ADDITION OF ATTRIBUTES

    def test_yota_manual_attributes(self):

        yota_object = lib.Convert.omm('y.drRQVI58c-E')
        yota_object.tags = ['interview','asia']
        yota_object.title = 'Koreans on Metoo'
        yota_object.update()
        self.assertEqual(yota_object.omm, 'y.drRQVI58c-E.Koreans_on_Metoo.interview.asia')

    def test_cue_manual_attributes(self):

        yota_object = lib.Convert.omm('y.drRQVI58c-E.5m')
        yota_object.tags = ['interview','asia']
        yota_object.title = 'Koreans on Metoo'
        yota_object.update()
        self.assertEqual(yota_object.omm, 'y.drRQVI58c-E.5m0s.Koreans_on_Metoo.interview.asia')

    def test_sample_manual_attributes(self):

        yota_object = lib.Convert.omm('y.drRQVI58c-E.5m.5m10s')
        yota_object.tags = ['interview','asia']
        yota_object.title = 'Koreans on Metoo'
        yota_object.update()
        self.assertEqual(yota_object.omm, 'y.drRQVI58c-E.5m0s.Koreans_on_Metoo.interview.asia.5m10s')
    

# YOTA TO CUE TO SAMPLE TO MIXTAPE TRAVERSAL
    
    def test_yota_to_cue_to_sample(self):
        yota_object = lib.Convert.omm('y.drRQVI58c-E')
        yota_object.tags = ['interview','asia']
        yota_object.title = 'Koreans on Metoo'
        yota_object.update()
        yota_object.omm += '.1m18s' # add time_start
        new = lib.Convert.omm(yota_object.omm)  # parse new Cue object
        test_str = 'y.drRQVI58c-E.1m18s.Koreans_on_Metoo.interview.asia'
        self.assertEqual(new.omm, test_str) # test for cue

    def test_cue_to_sample(self):
        test_cue = lib.Convert.omm('y.drRQVI58c-E.Koreans_on_Metoo.interview.asia.1m18s')
        test_cue.omm += '.2m'
        newer = lib.Convert.omm(test_cue.omm)
        test_str = 'y.drRQVI58c-E.1m18s.Koreans_on_Metoo.interview.asia.2m0s'
        self.assertEqual(newer.omm, test_str) # test for sample

    def test_sample_to_mixtape(self):
        test_sample = lib.Convert.omm('y.drRQVI58c-E.1m18s.Koreans_on_Metoo.interview.asia.2m0s')
        mixtape = test_sample.omm + '.' + test_sample.omm
        mix_obj = lib.Convert.omm(mixtape)
        test_str = 'y.drRQVI58c-E.1m18s.Koreans_on_Metoo.interview.asia.2m0s.y.drRQVI58c-E.1m18s.Koreans_on_Metoo.interview.asia.2m0s'
        self.assertEqual(mix_obj.omm_oneline(), test_str)


# MIXTAPE WITH ONLY YOTA AND CUE

    def test_mixtape_with_only_yotas(self):
        yota_object = lib.Convert.omm('y.drRQVI58c-E.y.NI1L8ZJgA9o')
        self.assertEqual(yota_object[1].omm, 'y.NI1L8ZJgA9o.MyYota')

    def test_mixtape_with_only_cues(self):
        yota_object = lib.Convert.omm('y.drRQVI58c-E.5m.y.NI1L8ZJgA9o.5m')
        self.assertEqual(yota_object[1].omm, 'y.NI1L8ZJgA9o.5m0s.MyCue')

    def test_mixtape_with_cue_and_yota(self):
        yota_object = lib.Convert.omm('y.drRQVI58c-E.y.NI1L8ZJgA9o.5m')
        self.assertEqual(yota_object[1].omm, 'y.NI1L8ZJgA9o.5m0s.MyCue')

    def test_mixtape_with_yota_and_cue(self):
        yota_object = lib.Convert.omm('y.drRQVI58c-E.5m.y.NI1L8ZJgA9o')
        self.assertEqual(yota_object[1].omm, 'y.NI1L8ZJgA9o.MyYota')


# MIXTAPE FROM FILE

    def test_mixtape_from_file_sample(self):
        yota_object = lib.Convert.omm('mixtapes/hackers2018.omm')
        self.assertEqual(yota_object[3].title, 'John Oliver: Trade')
    
    def test_mixtape_from_file_length(self):
        yota_object = lib.Convert.omm('mixtapes/hackers2018.omm')
        self.assertEqual(len(yota_object.content), 4)


# YOTA ARITHMETIC

    def test_yota_plus_yota_equals_mixtape(self):
        yota_object = lib.Convert.omm('y.drRQVI58c-E')
        yota_object2 = lib.Convert.omm('y.NI1L8ZJgA9o')
        mixtape_object = yota_object + yota_object2
        self.assertEqual(mixtape_object[1].omm, 'y.NI1L8ZJgA9o.MyYota')

    def test_cue_plus_cue_equals_mixtape(self):
        cue_object = lib.Convert.omm('y.drRQVI58c-E.5m')
        cue_object2 = lib.Convert.omm('y.NI1L8ZJgA9o.7m')
        mixtape_object = cue_object + cue_object2
        self.assertEqual(mixtape_object[1].omm, 'y.NI1L8ZJgA9o.7m0s.MyCue')

    def test_sample_plus_sample_equals_mixtape(self):
        yota_object = lib.Convert.omm('y.drRQVI58c-E.5m.6m')
        yota_object2 = lib.Convert.omm('y.NI1L8ZJgA9o.7m.8m')
        mixtape_object = yota_object + yota_object2
        self.assertEqual(mixtape_object[1].omm, 'y.NI1L8ZJgA9o.7m0s.MySample.8m0s')


    def test_yota_plus_cue_equals_mixtape(self):
        yota_object = lib.Convert.omm('y.drRQVI58c-E')
        yota_object2 = lib.Convert.omm('y.NI1L8ZJgA9o.7m')
        mixtape_object = yota_object + yota_object2
        self.assertEqual(mixtape_object[1].omm, 'y.NI1L8ZJgA9o.7m0s.MyCue')

    def test_cue_plus_yota_equals_mixtape(self):
        yota_object = lib.Convert.omm('y.drRQVI58c-E.7m')
        yota_object2 = lib.Convert.omm('y.NI1L8ZJgA9o')
        mixtape_object = yota_object + yota_object2
        self.assertEqual(mixtape_object[1].omm, 'y.NI1L8ZJgA9o.MyYota')

    def test_cue_plus_sample_equals_mixtape(self):
        yota_object = lib.Convert.omm('y.drRQVI58c-E.5m')
        yota_object2 = lib.Convert.omm('y.NI1L8ZJgA9o.7m.8m')
        mixtape_object = yota_object + yota_object2
        self.assertEqual(mixtape_object[1].omm, 'y.NI1L8ZJgA9o.7m0s.MySample.8m0s')

    def test_sample_plus_cue_equals_mixtape(self):
        yota_object = lib.Convert.omm('y.drRQVI58c-E.5m.6m3s')
        yota_object2 = lib.Convert.omm('y.NI1L8ZJgA9o.7m')
        mixtape_object = yota_object + yota_object2
        self.assertEqual(mixtape_object[1].omm, 'y.NI1L8ZJgA9o.7m0s.MyCue')

    def test_sample_plus_yota_equals_mixtape(self):
        yota_object = lib.Convert.omm('y.drRQVI58c-E.5m.6m3s')
        yota_object2 = lib.Convert.omm('y.NI1L8ZJgA9o')
        mixtape_object = yota_object + yota_object2
        self.assertEqual(mixtape_object[1].omm, 'y.NI1L8ZJgA9o.MyYota')

    def test_yota_plus_sample_equals_mixtape(self):
        yota_object = lib.Convert.omm('y.drRQVI58c-E')
        yota_object2 = lib.Convert.omm('y.NI1L8ZJgA9o.4m10s.4m30s')
        mixtape_object = yota_object + yota_object2
        self.assertEqual(mixtape_object[1].omm, 'y.NI1L8ZJgA9o.4m10s.MySample.4m30s')


    def test_mixtape_plus_yota_equals_mixtape(self):
        yota_object = lib.Convert.omm('y.drRQVI58c-E.y.drRQVI58c-E')
        yota_object2 = lib.Convert.omm('y.NI1L8ZJgA9o')
        mixtape_object = yota_object + yota_object2
        self.assertEqual(mixtape_object[2].omm, 'y.NI1L8ZJgA9o.MyYota')

    def test_mixtape_plus_cue_equals_mixtape(self):
        yota_object = lib.Convert.omm('y.drRQVI58c-E.y.drRQVI58c-E')
        yota_object2 = lib.Convert.omm('y.NI1L8ZJgA9o.4m10s')
        mixtape_object = yota_object + yota_object2
        self.assertEqual(mixtape_object[2].omm, 'y.NI1L8ZJgA9o.4m10s.MyCue')
    
    def test_mixtape_plus_sample_equals_mixtape(self):
        yota_object = lib.Convert.omm('y.drRQVI58c-E.y.drRQVI58c-E')
        yota_object2 = lib.Convert.omm('y.NI1L8ZJgA9o.4m10s.4m30s')
        mixtape_object = yota_object + yota_object2
        self.assertEqual(mixtape_object[2].omm, 'y.NI1L8ZJgA9o.4m10s.MySample.4m30s')

    def test_mixtape_plus_mixtape_equals_mixtape(self):
        yota_object = lib.Convert.omm('y.drRQVI58c-E.y.drRQVI58c-E')
        yota_object2 = lib.Convert.omm('y.drRQVI58c-E.y.drRQVI58c-E')
        mixtape_object = yota_object + yota_object2
        self.assertEqual(mixtape_object[3].omm, 'y.drRQVI58c-E.MyYota')

    def test_mixtape_slicing(self):
        yota_str = 'y.NI1L8ZJgA9o.4m10s.First Clip.4m30s.y.NI1L8ZJgA9o.5m10s.Second Clip.5m30s.y.NI1L8ZJgA9o.6m10s.Third Clip.6m30s'
        yota_object = lib.Convert.omm(yota_str)
        new_object = yota_object[1:]
        self.assertEqual(len(new_object.content), 2)

    def test_sample_indexing(self):
        yota_object = lib.Convert.omm('y.NI1L8ZJgA9o.10s.MySample.30s')
        new_object = yota_object[10]
        self.assertEqual(new_object.time_start, 20)

    
## PADDING AND SHIFTING

    def test_cue_shift_forwards(self):
        yota_object = lib.Convert.omm('y.youtubehash.5s')
        new_object = yota_object.shift(5)
        self.assertEqual(new_object.omm, 'y.youtubehash.10s.MyCue')

    def test_cue_shift_backwards(self):
        yota_object = lib.Convert.omm('y.youtubehash.10s')
        new_object = yota_object.shift(-5)
        self.assertEqual(new_object.omm, 'y.youtubehash.5s.MyCue')

    def test_sample_pad_front(self):
        yota_object = lib.Convert.omm('y.youtubehash.5s.10s')
        new_object = yota_object.pad(1)
        self.assertEqual(new_object.omm, 'y.youtubehash.4s.MySample.10s')

    def test_sample_pad_back(self):
        yota_object = lib.Convert.omm('y.youtubehash.5s.10s')
        new_object = yota_object.pad(-1)
        self.assertEqual(new_object.omm, 'y.youtubehash.5s.MySample.11s')


## YOTA SRT SEARCH

    def test_srt_search(self):
        url = 'https://www.youtube.com/watch?v=Utu0RNjf_h8'
        myYota = lib.Convert.omm(url)
        mentions = myYota.srt_search('kitchen')
        self.assertEqual(len(mentions.content), 2)
    def test_srt_search_2(self):
        url = 'https://www.youtube.com/watch?v=Utu0RNjf_h8'
        myYota = lib.Convert.omm(url)
        mentions = myYota.srt_search('kitchen')
        self.assertEqual(mentions[1].omm, 'y.Utu0RNjf_h8.6m23s.MyYota_keyword_kitchen_2.6m33s')


## BIT OBJECT PARSING

    def test_yota_with_sample_bit(self):
        YotaWithSampleBit = 'y._QYngRrbsKo.My_YouTube_Clip.b.2TKY42w.1s.SecNow.mp3.security.podcast.25s'
        self.assertEqual( lib.Convert.omm(YotaWithSampleBit).bits[0].omm, 'b.2TKY42w.1s.SecNow.mp3.security.podcast.25s')
        self.assertEqual( lib.Convert.omm(YotaWithSampleBit).bits[0].title, 'SecNow')
    def test_yota_with_tag_and_sample_bit(self):
        YotaWithTagAndSampleBit = 'y._QYngRrbsKo.My_YouTube_Clip.video.b.2TKY42w.Security_Now.mp3.security.podcast.1s.25s'
        self.assertEqual( lib.Convert.omm(YotaWithTagAndSampleBit).title, 'My YouTube Clip')
        self.assertEqual( lib.Convert.omm(YotaWithTagAndSampleBit).bits[0].title, 'Security Now')
    def test_yota_with_bit(self):
        YotaWithBit = 'y._QYngRrbsKo.My_YouTube_Clip.video.b.2TKY42w.Security_Now.security.podcast'
        self.assertEqual( lib.Convert.omm(YotaWithBit).tags, ['video'])
    def test_yota_with_tags(self):
        YotaWithTags = 'y._QYngRrbsKo.My_YouTube_Clip.tags.video'
        self.assertEqual( lib.Convert.omm(YotaWithTags).tags, ['tags','video'])
    def test_cue_with_tags(self):
        CueWithTags = 'y._QYngRrbsKo.My_YouTube_Clip.tags.video.1m'
        self.assertEqual( lib.Convert.omm(CueWithTags).url, 'https://www.youtube.com/embed/_QYngRrbsKo?start=60&rel=0&autoplay=1')
    
    def test_sample_with_tags(self):
        SampleWithTags = 'y._QYngRrbsKo.My_YouTube_Clip.tags.video.1m.2m'
        self.assertEqual( lib.Convert.omm(SampleWithTags).url, 'https://www.youtube.com/embed/_QYngRrbsKo?start=60&end=120&rel=0&autoplay=1')


## BIT OBJECTS IN __REPR__
    
    def test_sample_with_bits_repr(self):

        mySampleWithBits = lib.Convert.omm('y._QYngRrbsKo.My_YouTube_Clip.video.1m1s.1m10s.b.2TKY42w.Sec_Now.security.podcast.b.2TKY42w.Sec_Now.mp3.security.podcast.6m1s.7m25s.b.2TKY42w.Sec_Now.mp3.security.podcast.8m1s.9m25s')
        self.assertEqual(mySampleWithBits.__repr__(), 'My YouTube Clip  (video)  9s  [Sec Now, Sec Now, Sec Now]')

    def test_cue_with_bits_repr(self):
        myCueWithBits = lib.Convert.omm('y._QYngRrbsKo.My_YouTube_Clip.1m1s.b.2TKY42w.Sec_Now.security.podcast.b.2TKY42w.Sec_Now.mp3.security.podcast.6m1s.7m25s.b.2TKY42w.Sec_Now.mp3.security.podcast.8m1s.9m25s')
        self.assertEqual(myCueWithBits.__repr__(), 'My YouTube Clip  [Sec Now, Sec Now, Sec Now]')

    def test_yota_with_bits_second_bit_omm(self):
        myYotaWithBits = lib.Convert.omm('y._QYngRrbsKo.My_YouTube_Clip.b.2TKY42w.Sec_Now.security.podcast.b.2TKY42w.Sec_Now.mp3.security.podcast.6m1s.7m25s.b.2TKY42w.Sec_Now.mp3.security.podcast.8m1s.9m25s')
        self.assertEqual(myYotaWithBits.__repr__(), 'My YouTube Clip  [Sec Now, Sec Now, Sec Now]')


## BIT ONLY PARSING

    # Bit.Link

    def test_bit_with_no_title_or_tags(self):
        bit_str = 'b.2NYwBFd'
        myBit = lib.Convert.omm(bit_str)
        self.assertEqual(myBit.bitly_hash, '2NYwBFd')

    def test_bit_with_no_title(self):
        bit_str = 'b.2NYwBFd.some.tags'
        myBit = lib.Convert.omm(bit_str)
        self.assertEqual(myBit.__repr__(), 'MyBit  (some, tags)')

    def test_bit_with_title_and_tags(self):
        bit_str = 'b.2NYwBFd.MyTitle.some.tags'
        myBit = lib.Convert.omm(bit_str)
        self.assertEqual(myBit.omm, 'b.2NYwBFd.MyTitle.some.tags')

    def test_bit_with_title(self):
        bit_str = 'b.2NYwBFd.MyTitle'
        myBit = lib.Convert.omm(bit_str)
        self.assertEqual(myBit.omm, 'b.2NYwBFd.MyTitle')

    def test_bit_custom_link(self):
        bit_str = 'b.sn-704'
        myBit = lib.Convert.omm(bit_str)
        self.assertEqual(myBit.link, 'http://twit.cachefly.net/audio/sn/sn0704/sn0704.mp3')


    # Bit.Mp3

    def test_bit_mp3_cue_no_title(self):
        bit_str = 'b.sn-704.5m.mp3'
        myBit = lib.Convert.omm(bit_str)
        self.assertEqual(myBit.time_start, 300)

    def test_bit_mp3_sample_no_title(self):
        bit_str = 'b.sn-704.5m.5m59s.mp3'
        myBit = lib.Convert.omm(bit_str)
        self.assertEqual(myBit.time(), '59s')

    def test_bit_mp3_type(self):
        bit_str = 'b.sn-704.mp3'
        myBit = lib.Convert.omm(bit_str)
        if isinstance(myBit, bit.Mp3):
            checked_out = True
        self.assertEqual(checked_out, True)

    def test_bit_mp3_sample_with_title(self):
        bit_str = 'b.sn-704.Security Now Quote.mp3.5m.2h'
        myBit = lib.Convert.omm(bit_str)
        self.assertEqual(myBit.title, 'Security Now Quote')

    def test_bit_mp3_cue_with_title(self):
        bit_str = 'b.sn-704.Security Now Quote.mp3.5m'
        myBit = lib.Convert.omm(bit_str)
        self.assertEqual(myBit.title, 'Security Now Quote')

    def test_bit_mp3_yota_with_title(self):
        bit_str = 'b.sn-704.Security Now Quote.mp3'
        myBit = lib.Convert.omm(bit_str)
        self.assertEqual(myBit.title, 'Security Now Quote')

    def test_bit_mp3_repr(self):
        bit_str = 'b.sn-704.Security Now Quote.mp3'
        myBit = lib.Convert.omm(bit_str)
        self.assertEqual(myBit.__repr__(), 'Security Now Quote  (mp3)')

    def test_bit_repr(self):
        bit_str = 'b.sn-704.Security Now Quote'
        myBit = lib.Convert.omm(bit_str)
        self.assertEqual(myBit.__repr__(), 'Security Now Quote')

##  Sample Subtraction

    def test_sample_subtraction(self):
        mySampleStr = 'y.Ufr7O0qtX9U.1s.1h30m'
        myBigSample = lib.Convert.omm(mySampleStr)
        mySmallSampleStr = 'y.Ufr7O0qtX9U.1h1m.1h2m'
        mySmallSample = lib.Convert.omm(mySmallSampleStr)
        firstBite, secondBite = myBigSample - mySmallSample
        self.assertEqual(firstBite.time(), '1h59s')
        self.assertEqual(secondBite.time(), '28m')


##  YOTA METHODS

    def test_yota_methods(self):
        myYotaStr = 'y.Ufr7O0qtX9U'
        myYota = lib.Convert.omm(myYotaStr)
        self.assertEqual(myYota.methods(), ['hash','iframe','methods','play','srt_search','to_sample','update','vlc'])

    def test_cue_methods(self):
        myCueStr = 'y.Ufr7O0qtX9U.1s'
        myCue = lib.Convert.omm(myCueStr)
        self.assertEqual(myCue.methods(), ['hash','iframe','methods','play','srt_search','to_sample','update','vlc'])

    def test_sample_methods(self):
        mySampleStr = 'y.Ufr7O0qtX9U.1s.10s'
        mySample = lib.Convert.omm(mySampleStr)
        self.assertEqual(mySample.methods()[:6], ['beta_format', 'beta_format_2', 'bits', 'first_name', 'format', 'hash'])

    def test_mixtape_methods(self):
        myCueStr = 'y.Ufr7O0qtX9U.1s.10s.y.Ufr7O0qtX9U.1s.10s'
        myCue = lib.Convert.omm(myCueStr)
        #print(myCue.methods()[:5])
        self.assertEqual(myCue.methods()[:5], ['add_tags', 'append', 'content', 'find', 'hash'])

    def test_bit_methods(self):
        myBitStr = 'b.sn-704.MyBit'
        myBit = lib.Convert.omm(myBitStr)
        self.assertEqual(myBit.methods(), ['hash','iframe', 'methods', 'play', 'update', 'vlc'])

    def test_bit_mp3_methods(self):
        myBitStr = 'b.sn-704.MyBit.mp3'
        myBit = lib.Convert.omm(myBitStr)
        self.assertEqual(myBit.methods(), ['hash','iframe', 'methods', 'play', 'time', 'update', 'vlc'])





if __name__ == '__main__':
    unittest.main()    
