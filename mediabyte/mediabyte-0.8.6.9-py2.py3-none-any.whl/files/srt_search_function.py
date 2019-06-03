
from . import srt_keyword_parser as srt
import subprocess, glob, os
from copy import deepcopy
from . import cnf
from . import dl2



def srt_search(self, omm, Mixtape, keyword, clip_length=10, do_not_combine_overlapping=False):

    #def check_cache(youtube_hash):
    # check if .srt is already downloaded, use cache version

    #     youtube_url = 'https://youtube.com/watch?v=' + youtube_hash        
    #     srt_filename = cnf.package_path + cnf.os_sep + 'srt' + cnf.os_sep + '*.srt'
    #     srt_files = glob.glob(srt_filename)

    #     for srt_filename in srt_files:
    #         if self.youtube_hash in srt_filename:
    #             return srt_filename
        
    # cache_result = check_cache(self.youtube_hash)
    # # use the cache subtitles if present
    # try:
    #     #cache_result is not None
    #     latest_file = cache_result
    # # or download if not
    # except:
    #     srt_filename = dl2.dl_srt(youtube_url)
    #     latest_file = srt_filename
    
    youtube_url = 'https://youtube.com/watch?v=' + self.youtube_hash
    srt_filename = dl2.dl_srt(youtube_url)
    result = srt.main(srt_filename, keyword)
    
    if len(result) > 1:
        myYota = omm(result[0])
        if clip_length:
            myYota = myYota.to_sample(omm, add=clip_length)
        myYota.title = self.title + ' keyword ' + keyword + ' 1'
        myYota.update()
        myMixtape = Mixtape(myYota)
        # print('startet Mixtape with object:', result[0])
        for i, item in enumerate(result[1:]):
            myYota = omm(item)
            if clip_length:
                myYota = myYota.to_sample(omm, add=clip_length)
            myYota.title = self.title + ' keyword ' + keyword + ' ' + str(i+2)
            myYota.update()
            myMixtape += myYota
            # print('added item:', item)
    
    elif len(result) == 1:
        myYota = omm(result[0])
        if clip_length:
            myYota = myYota.to_sample(omm, add=clip_length)
        myYota.title = self.title + ' keyword ' + keyword + ' 1'
        myYota.update()
        myMixtape = Mixtape(myYota)

    elif len(result) == 0:
        myMixtape = None


    def combine_overlapping(inMix):
        result = []
        skip_next = False
        for i, item in enumerate(inMix[:-1]):
            if skip_next == True:
                skip_next = False
                continue
            test = item.time_end > inMix[i+1].time_start
            test2 = item.youtube_hash == inMix[i+1].youtube_hash
            if test and test2:
                #print(item.time_end, inMix[i+1].time_start)
                newSample = deepcopy(item)
                newSample.time_end = inMix[i+1].time_end
                newSample.update()
                result.append(newSample)
                skip_next = True
            else:
                result.append(item)
        
        if skip_next == False:
            result.append(inMix[-1])
        myMix = Mixtape(result[0])
        uniques = []
        for item in result:
            if item not in uniques:
                uniques.append(item)
        # NB: Hacky solution, filtering doubled results (coming from where?)
        for item in uniques[1:]:
            myMix += item
        return(myMix)
    

    if not do_not_combine_overlapping:
        if isinstance(myMixtape, Mixtape) and len(myMixtape.content) > 1:
            # NB: Hacky, overconfident in its own success
            while True:
                if len(myMixtape.content) > 1:
                    myNewMixtape = combine_overlapping(myMixtape)
                    if myNewMixtape.omm() == myMixtape.omm():
                        return(myNewMixtape)
                    else:
                        myMixtape = myNewMixtape
                else:
                    return(myMixtape)

    return(myMixtape)
