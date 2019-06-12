import pyperclip

class ClipboardSQLFormatter(object):
    
    def __init__(self):
        pass
    
    def get_clipboard_input(self):
        input("Copy text to be formatted, then type whatever you want because it don't matter. None of this matters. Then press Enter.")
        return pyperclip.paste()
        
    def split_string(self, s,sep='\r\n'):
        return s.split(sep)
    
    def build_sql_list(self,col_list, prefix="'", suffix="',"):
        for i, c in enumerate(col_list[:-1]):
            col_list[i] = prefix+c+suffix
        col_list[-1] = prefix+col_list[-1]+suffix[:-1]
        return col_list
        
    def write_to_clipboard(self, col_list, sep='\r\n'):
        pyperclip.copy(sep.join(col_list))
        
    def run_it(self):
        '''
        Make sure you pronounce this in Uttam's voice.
        '''
        bad_string = self.get_clipboard_input()
        col_list = self.split_string(bad_string)
        formatted_list = self.build_sql_list(col_list)
        print("This will be copied to your clipboard:")
        for c in formatted_list:
            print(c)
        self.write_to_clipboard(formatted_list)