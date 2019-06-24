class PropertyMapper:
    def to_dict(self):
        dt = {}
        for name in dir(self.__class__):
            po = getattr(self.__class__, name)
            if isinstance(po, property):
                field_name = name
                if po.__doc__ is not None:
                    dict_map_str = "::dict:map "
                    for line in po.__doc__.splitlines():
                        pos = line.find(dict_map_str)
                        if pos >= 0:
                            field_name = line[pos + len(dict_map_str):]
                dt[field_name] = getattr(self, name)
        return dt
