

def tail_file(file_path, line_count=10):
  """
  Returns the last lines of file.
  """

  line_list = []
  with open(file_path) as f:
    BUFSIZ = 1024
    f.seek(0, 2)
    bytes = f.tell()
    size = line_count + 1
    block = -1
    while size > 0 and bytes > 0:
      if bytes - BUFSIZ > 0:
          # Seek back one whole BUFSIZ
          f.seek(block * BUFSIZ, 2)
          line_list.insert(0, f.read(BUFSIZ))
      else:
          f.seek(0, 0)
          # only read what was not read
          line_list.insert(0, f.read(bytes))
      line_len = line_list[0].count('\n')
      size -= line_len
      bytes -= BUFSIZ
      block -= 1

  return '\n'.join(''.join(line_list).splitlines()[-line_count:])