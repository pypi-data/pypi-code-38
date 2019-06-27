import datetime
from swutil.misc import no_context
        
class Log:   
    def __init__(self,print_filter=True,write_filter=False,file_name=None,lock=None):
        if print_filter is True:
            print_filter = lambda _: True
        if print_filter is False:
            print_filter = lambda _: False
        self.print_filter=print_filter
        self.file_name=file_name
        if write_filter and not self.file_name:
            raise ValueError('Specify file_name to write log in file')
        if write_filter is True:
            write_filter = lambda _: True
        if write_filter is False:
            write_filter = lambda _: False
        self.write_filter=write_filter
        self.entries=[]
        self.lock=lock
       
    def __call__(self,*messages,group = None,tags = None):
        if len(messages)==1:
            messages = messages[0]
        self.log(message=messages,group=group,tags=tags) 
    def log(self,message=None,group=None,tags=None,use_lock=True):
        def foo():
            entry=Entry(group=group,message=message,tags=tags)
            self.entries.append(entry)
            if self.print_filter(entry):
                print(entry)
            if self.write_filter(entry):
                with open(self.file_name,'a') as fp:
                    fp.write(str(entry)+'\n')
        with self.lock if (self.lock is not None and use_lock) else no_context():
            foo()
    
    def print_log(self,print_filter=None):
        print(self.__str__(print_filter))
      
    def __str__(self,print_filter=None):
        print_filter=print_filter or self.print_filter
        return '\n'.join([str(entry) for entry in self.entries if print_filter(entry)])

        
def filter_generator(require_group=None,require_tags=None,require_message=None,exclude_group=None,exclude_tags=None,exclude_message=None):
    def filter(entry):  # @ReservedAssignment
        if require_group is None:
            require_group=[]
        else:
            if not type(require_group) is list:
                require_group=[require_group]
        if require_tags is None:
            require_tags=[]
        else:
            if not type(require_tags) is list:
                require_tags=[require_tags]
        if require_message is None:
            require_message=[]
        else:
            if not type(require_message) is list:
                require_message=[require_message]         
        if exclude_group is None:
            exclude_group=[]
        else:
            if not type(exclude_group) is list:
                exclude_group=[exclude_group]
        if exclude_tags is None:
            exclude_tags=[]
        else:
            if not type(exclude_tags) is list:
                exclude_tags=[exclude_tags]
        if exclude_message is None:
            exclude_message=[]
        else:
            if not type(exclude_message) is list:
                exclude_message=[exclude_message]
        return  (
                    (any([group == entry.group for group in require_group]) or not require_group)
                    and 
                    all([tag in entry.tags for tag in require_tags])
                    and 
                    all([message in entry.message for message in require_message])
                    and
                    not entry.group in exclude_group
                    and
                    all([tag not in entry.tags for tag in exclude_tags])
                    and
                    all([message not in entry.message for message in exclude_message])
                )
    return filter
    
class Entry:
    def __init__(self,group=None,message=None,tags=None):
        if group is None:
            self.group=''
        else:
            self.group=group
        if message is None:
            self.message=''
        else:
            self.message=message
        if tags is None:
            self.tags=[]
        else:
            self.tags=tags
        self.time=datetime.datetime.now()
        
    def __str__(self):
        string='<'+self.time.strftime("%y-%m-%d %H:%M:%S")
        if self.group:
            string+= ' | '+ self.group
        string+='> '+str(self.message)
        return string
