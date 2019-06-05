from mdjpp.options import makedate, maketime

class Tag(object):
    """
    Abstract tag.
    """
    def __init__(self,value):
        """
        :param value: Value of tag.
        """
        self.value = value
        self.body = []
        
    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__, str(self.value))

    def __repr__(self):
        return self.__str__()
                
    def __eq__(self,other):
        return self.value == other.value
        
    def printme(self,line):
        return self.body.append(line)

class NoTag(Tag):
    """
    No tag.
    """
    def __init__(self,dummy=None):
        """
        :param str dummy: Value of no tag.
        """
        super().__init__(dummy)
    

class Date(Tag):
    """
    Date tag.
    """
    def __init__(self,date):
        """
        :param datetime.date date: Date of this tag.
        """
        super().__init__(date)

class Time(Tag):
    """
    Time tag.
    """
    def __init__(self,time):
        """
        :param datetime.time time: Time of this tag.
        """
        super().__init__(time)

    
class Verbatim(Tag):
    """
    Verbaim tag.
    """
    def __init__(self,name):
        """
        :param str name: Name of this tag.
        """
        super().__init__(name)


class Multi(Tag):
    """
    Multiple verbatim tag.
    """
    def __init__(self,tags):
        """
        :param list tags: Tuple of :class:`Verbatim` tags.
        """
        super().__init__(tags)
    
    def append(self,tag):
        """
        :param tag: Verbatim or Mulit tag to add to the current tag.
        """
        if isinstance(tag,Verbatim):
            self.value.append(tag)
        elif isinstance(tag,Multi):
            self.value.extend(tag.value)


class Global(Multi):
    """
    Global Multiple verbatim tag.
    """
    def __init__(self,mtag):
        """
        :param class:`Multi` mtag: Input class:`Multi` tag.
        """
        super().__init__(mtag.value)
        


def istag(line):
    """
    :param str line: Input line to check
    :retrun: True if input line is a tag, i.e. starts with `@@`; otherwise returns False.
    :rtype: bool
    """
    return line.startswith('@@') and len(line)>2


def maketag(line):
    """
    :param str line: Input tag line.
    :return: Tag of Data, Time, or Verbatim type.
    :rtype: Tag
    """
    assert istag(line)
    line = line[2:]
    # is date?
    date = makedate(line)
    if date:
        return Date(date)
    # is time?
    time = maketime(line)
    if time:
        return Time(time)
    # make Multi tag
    return Multi([Verbatim(line)])
    
    
