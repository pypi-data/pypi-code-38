import sys
from util.file_handler import FileHandler 

handler = FileHandler(sys.argv[1])
handler.write(sys.argv[2:])
