class InputParser:
    def __init__(self, key_down_callback=None, key_up_callback=None, keys_down=None, new_key_down_callback=None):
        if keys_down is None:
            self.keys_down = set()
        else:
            self.keys_down = keys_down

        self.key_down_callback = key_down_callback
        self.key_up_callback = key_up_callback
        self.new_key_down_callback = new_key_down_callback

    def process_keyboard_event(self, event, verbose=False):
        # print(event)
        nCode, e = event
        key_code = e.key_code  # DWORD = 32bit: ffff ffff
        key_code_special = 0
        key_name = hex(e.key_code)[2:]
        key_code_special = int((e.key_code & 0xFF00000000) / 0x100000000)
        if verbose:
            print('type:', e.event_type)
            print(' key:', hex(e.key_code))
            print('scan:', hex(e.scan_code))
            print(' alt:', e.alt_pressed)
            print('\n\n')

        special = False
        import win_key_hook.key_map as key_map
        try:
            key_name = key_map.key_code_map[key_code]
        except KeyError:
            try:
                key_name = key_map.key_code_map[e.key_code]
            except KeyError:
                try:
                    key_name = key_map.key_code_special_map[key_code_special]
                    special = True
                except KeyError:
                    pass

        if e.event_type == 'key down':
            return self.on_key_down(key_name, special)
        else:
            return self.on_key_up(key_name)

    def on_key_down(self, key_name, is_special_key):
        print(key_name, end='', flush=True)
        if key_name not in self.keys_down:
            self.keys_down.add(key_name)
            if self.new_key_down_callback is not None:
                self.new_key_down_callback(key_name)

        if self.key_down_callback is not None:
            return self.key_down_callback(key_name)

        return True

    def on_key_up(self, key_name):
        try:
            self.keys_down.remove(key_name)
        except KeyError as ke:
            print('\nkey error:', ke)
        except Exception as ex:
            import travel_backpack
            print(travel_backpack.format_exception_string(ex))

        if self.key_up_callback is not None:
            return self.key_up_callback(key_name)

        return True