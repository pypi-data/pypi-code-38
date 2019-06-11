import gzip
import zlib
import io
from ssxtd import parsers

import time

my_file = io.StringIO('''<doc farm = "456"> 
    <i species = "lapin" sex = "male" >John</i>
    <i species = "chien"><sub subspec = "Kooikerhondje">Tristan</sub></i>
    <i species = "cheval">
        <count>1.1</count>
    </i>
	<i>
        <month>11</month>
        <year>2011</year>
        <day>1</day>
    </i>
</doc>
''')



def try_conversion(value):
    """called when encountering a string in the xml
    
    Arguments:
        value {str} -- value to be converted, if possible
    
    Returns:
        [str, float, int] -- converted value
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        pass
    try:
        return float(value)
    except (ValueError, TypeError):
        pass
    return value

# {'#alldata': [{'month': {'#alldata': ['09']}}, {'year': {'#alldata': ['1993']}}, {'day': {'#alldata': ['09']}}]}
def merge_date_tags(path, k):
    """called when encountering only tags in an element ( no text, nor mixed tag and text)
    
    Arguments:
        path {list} -- path of the element containing the tags
        k {string} -- name of the element containing the tags
    
    Returns:
        whatever type you want -- the value of the element
        note : if you want 
    """
    
    l=k['#alldata']

    #2015/01/01 12:10:30
    # if "PubMedPubDate" in path[-1]:
    if "date" in path[-1].lower():
        month=None
        year=None
        day=None
        hour=None
        minute=None
        r=""
    
        # it should always be a dict with one key, and a subdict as value, containing  an "#alldata" key
        # {'month': {'#alldata': ['09']}}
        for i in l:
                # month
                k = next(iter(i))
                # ['09']
                ad = i[k]['#alldata']
                
                if k == "Year" and len(ad) == 1 and isinstance (ad[0], str):
                        year=ad[0]
                elif k == "Month" and len(ad) == 1 and isinstance (ad[0], str):
                        month=ad[0]
                elif k == "Day" and len(ad) == 1 and isinstance (ad[0], str):
                        day=ad[0]
                elif k == "Hour" and len(ad) == 1 and isinstance (ad[0], str):
                        hour=ad[0]
                        if len(hour) == 1:
                                hour = "0"+hour
                elif k == "Minute" and len(ad) == 1 and isinstance (ad[0], str):
                        minute=ad[0]
                        if len(minute) == 1:
                                minute = "0"+minute
        if year is not None:
            r=r+year
            if month is not None:
                r=r+"/"+month
                if day is not None:
                    r=r+"/"+day
                    if hour is not None:
                        r=r+ " "+hour
                        if minute is not None:
                            r=r+":"+minute
            #retrun only if at least "year" is present
            return r
    return k



def month_to_num(m):
    try:
        int(m)
    except (ValueError, TypeError):
        return{
                'Jan' : "01",
                'Feb' : "02",
                'Mar' : "03",
                'Apr' : "04",
                'May' : "05",
                'Jun' : "06",
                'Jul' : "07",
                'Aug' : "08",
                'Sep' : "09", 
                'Oct' : "10",
                'Nov' : "11",
                'Dec' : "12"
        }[m]

    return m


print("lxml_parse :")

for i in parsers.lxml_parse(my_file, depth=2, compression=None, value_processor=try_conversion, object_processor=merge_date_tags):
    print(i)