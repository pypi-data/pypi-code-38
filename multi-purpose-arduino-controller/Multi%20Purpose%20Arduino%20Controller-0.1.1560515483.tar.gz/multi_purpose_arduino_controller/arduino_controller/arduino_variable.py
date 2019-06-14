import collections

arduino_var_to_struc = collections.namedtuple('arduino_var_to_struc',
                                              'struct minimum maximum arduino_setter arduino_getter python_type html_input default_value byte_size')
arduino_var_to_struc_available = {
    'uint8_t': arduino_var_to_struc(struct="B", minimum=0, maximum=2 ** 8 - 1, arduino_setter="{{ardvar_name}}=data[0];",python_type=int, html_input='number',default_value=0,arduino_getter='write_data({{ardvar_name}},{BYTEID});', byte_size=1),
    'uint16_t': arduino_var_to_struc(struct="I", minimum=0, maximum=2 ** 16 - 1, arduino_setter="uint16_t temp;memcpy(&temp,data,2);{{ardvar_name}}=temp;",python_type=int, html_input='number',default_value=0,arduino_getter='write_data({{ardvar_name}},{BYTEID});', byte_size = 2),
    'uint32_t': arduino_var_to_struc(struct="L", minimum=0, maximum=2 ** 32 - 1, arduino_setter="uint32_t temp;memcpy(&temp,data,4);{{ardvar_name}}=temp;",python_type=int, html_input='number',default_value=0,arduino_getter='write_data({{ardvar_name}},{BYTEID});', byte_size = 4),
    'uint64_t': arduino_var_to_struc(struct="Q", minimum=0, maximum=2 ** 64 - 1, arduino_setter="uint64_t temp;memcpy(&temp,data,8);{{ardvar_name}}=temp;",python_type=int, html_input='number',default_value=0,arduino_getter='write_data({{ardvar_name}},{BYTEID});', byte_size = 8),
}


class StrucTypeNotFoundException(Exception): pass


class arduio_variable:
    def __init__(self, name, getter=None, setter=None, type='uint8_t', eeprom=False, default=None, sendtype=None,
                 receivetype=None, minimum=None, maximum=None, is_data_point=False,
                 python_type=None,html_input=None,arduino_getter=None,arduino_setter=None,byte_size=None,save=True):
        self.save = save
        self.is_data_point = is_data_point

        self.name = name
        self.eeprom = eeprom
        self.type = type
        try:
            ard_var=arduino_var_to_struc_available.get(type)
            self.receivetype = ard_var.struct if receivetype is None else receivetype
            self.sendtype = ard_var.struct if sendtype is None else sendtype
            self.maximum = ard_var.maximum if maximum is None else maximum
            self.minimum = ard_var.minimum if minimum is None else minimum

            self.byte_size = ard_var.byte_size if byte_size is None else byte_size
            
            self.arduino_setter = None if arduino_setter is False else (ard_var.arduino_setter.replace("{{ardvar_name}}",self.name) if arduino_setter is None else arduino_setter)
            self.arduino_getter = None if arduino_getter is False else (ard_var.arduino_getter.replace("{{ardvar_name}}",self.name) if arduino_getter is None else arduino_getter)

            self.python_type = arduino_var_to_struc_available.get(
                type).python_type if python_type is None else python_type

            self.html_input = '<input type='+ard_var.html_input+' min="'+str(self.minimum)+'" max="'+str(self.maximum)+'" value="{{value}}"'+(' readonly' if self.arduino_setter is None else '')+'>' if html_input is None else html_input
            self.default = ard_var.default_value if default is None else default
        except AttributeError:
            raise StrucTypeNotFoundException('Struct equivalent not found for ' + str(type) + ' please define manually')

#        if eeprom:
 #           self.arduino_setter=self.arduino_setter+""

        self.value = self.default
        self.setter = None if setter is False else (self.default_setter if setter is None else setter)
        self.getter = None if setter is False else (self.default_getter if getter is None else getter)

    def default_getter(self, instance):
        return self.value

    def default_setter(self, instance, data, send_to_board=True):
        if data is None: return
        data = self.python_type(data)
        if data < self.minimum: data = self.minimum
        if data > self.maximum: data = self.maximum
        if self.arduino_setter is not None:
            if send_to_board:
                instance.get_portcommand_by_name("set_"+self.name).sendfunction(data)
        self.value = data
        if self.is_data_point:
            instance.datapoint(self.name,data)

    def __set__(self, instance, value):
        self.setter(instance, value)

    def __get__(self, instance, owner):
        return self.getter(instance)

    def set_without_sending_to_board(self, instance, data):
        self.setter(instance, data, send_to_board=False)
