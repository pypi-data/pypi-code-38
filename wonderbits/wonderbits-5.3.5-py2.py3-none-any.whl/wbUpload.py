from .wbits import Wonderbits

class WBUpload(Wonderbits):
    def __init__(self, index = 1):
        Wonderbits.__init__(self)
        self.index = index

    
    def upload_with_file_path(self, file_path):
        if not self._is_empty(file_path):
            try:
                code = ''
                with open(file_path,'r') as f:
                    code = ''.join(f.readlines())
                if not self._is_empty(code):
                    self._set_raw_command(b'\x05')
                    self._set_command(code)
                    self._set_raw_command(b'\x04')
            except Exception as e:
                print(file_path, '文件不存在！')
                print(e)



    def upload_with_file_content(self, file_content):
        if not self._is_empty(file_content):
            self._set_raw_command(b'\x05')
            self._set_command(file_content)
            self._set_raw_command(b'\x04')
    
    
    def _is_empty(self, arg):
        is_empty = False
        if not arg:
            is_empty = True
            print('参数不可以为空!')
        return is_empty