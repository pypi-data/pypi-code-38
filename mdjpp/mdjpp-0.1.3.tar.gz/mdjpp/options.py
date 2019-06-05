import datetime as dt


def makedate(line):
    if len([d for d in line if d in '0123456789']) == 8:
        return dt.date(int(line[:4]),int(line[4:6]),int(line[6:]))
        

def maketime(line):
    if len([d for d in line if d in ':0123456789']) == 5:
        return dt.time(int(line[:2]),int(line[3::]))
        

class TagsFilters(object):
    
    mdjpp_skip_notag_content = False
    mdjpp_skip_global_tag_content = False
    
    mdjpp_date_from = ""
    mdjpp_date_to = ""
    
    mdjpp_date_skip_notags = False
    mdjpp_date_skip_empty = False
    
    mdjpp_skip_tag = ""
    mdjpp_only_tag = ""
    mdjpp_only_global_tag = ""


class Render(object):
    
    mdjpp_html = False
    mdjpp_null = True
    mdjpp_md = False
   


class mdJPP(TagsFilters,Render):
    
    def reparse_options(self):
        
        # date
        if self.mdjpp_date_from:
            self.mdjpp_date_from = makedate(self.mdjpp_date_from)
        if self.mdjpp_date_to:
            self.mdjpp_date_to = makedate(self.mdjpp_date_to)
        # render
        if not (self.mdjpp_html or self.mdjpp_md):
            self.mdjpp_null = True
    
default_options = mdJPP()

