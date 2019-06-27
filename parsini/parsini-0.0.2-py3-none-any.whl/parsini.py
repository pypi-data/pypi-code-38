# -*- coding: utf-8 -*-
#!/usr/bin/env python3

class Parsini:
    def __init__(self, configfile):
        self.configfile= configfile
        self.rawfile= []
        self.config_dict= {}


    def read(self):
        # create list
        with open(self.configfile) as filec:
            for filel in filec:
                self.rawfile.append(filel)

        # create config dict
        section=None
        for config_line in self.rawfile:
            equal= config_line.find('=')

            # sections
            if config_line.find('[')!=-1:
                section=  config_line [config_line.find('[')+1 : config_line.find(']')]
                self.config_dict[section]={}

            # name, values
            elif config_line!='' and equal!=-1:
                name= config_line [0:equal].strip()
                comm_inline= config_line.find('#')
                if comm_inline!=-1:
                    value= config_line [equal+1:comm_inline].strip()
                else:
                    value= config_line [equal+1:].strip()
                try:
                    value= int(value)
                except ValueError:
                    try:
                        value= float(value)
                    except:
                        value= str(value)
                self.config_dict[section].update([(name , value)])
            else:
                pass
        return self.config_dict


    def get_param(self, section, name):
        section= self.config_dict.get(section)
        return section.get(name)


    def set_param(self, section, name, new_value):
        old_value= self.get_param(section, name)

        section_flag= False
        for i in range(len(self.rawfile)):
            if section in self.rawfile[i]: section_flag= True
            if section_flag== True:
                self.rawfile[i]= self.rawfile[i].replace(str(old_value), str(new_value))

        #actulizar el dict
        self.config_dict[section].update([(name , new_value)])
        return True


    def create_param(self, section, name, value):
        # update dict
        if self.config_dict.get(section)==None:
            self.config_dict[section]={}
            self.rawfile.append('\n['+section+']\n')

        self.config_dict[section].update([(name , value)])

        for i, l in list(enumerate(self.rawfile)):
            if '['+section+']' in l:
                self.rawfile.insert(i+1, name+" = {}\n".format(value))


    def write(self, config_file= None):
        if config_file== None: config_file= self.configfile
        config_file= open(config_file, 'w')
        config_file.writelines(self.rawfile)
        config_file.close
        return True


    def get_rawlist(self):
        return self.rawfile


    def get_confidict(self):
        return self.config_dict
