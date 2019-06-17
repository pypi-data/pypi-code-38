__author__ = 'rcj1492'
__created__ = '2017.05'
__license__ = 'MIT'

def load_ignore(vcs='git', type='service'):

    ''' a method to retrieve the module template vcs ignore text '''

    # retrieve module path
    from os import path
    from pocketlab import __module__
    from importlib.util import find_spec
    module_path = find_spec(__module__).submodule_search_locations[0]
    file_text = ''

    # retrieve file text
    if vcs.lower() in ('git', 'mercurial'):
        file_name = 'models/gitignore'
        if type.lower() == 'python':
            file_name += '.python'
        elif type.lower() == 'node':
            file_name += '.node'
        else:
            file_name += '.service'
        file_name += '.txt'
        file_path = path.join(module_path, file_name)
        file_text = open(file_path).read()
    # modify file
    if vcs.lower() == 'mercurial':
        import re
        wildcard_regex = re.compile('\n\*\.')
        file_text = wildcard_regex.sub('\n.', file_text)
        file_regex = re.compile('\n\..*')
        file_text = file_regex.sub(lambda x: '%s$' % x.group(0) if x.group(0).find('/') == -1 else x.group(0), file_text)
        file_text = file_text.replace('.', '\.')
        file_text = file_text.replace('\.gitignore', ' .hgignore')
    elif vcs.lower() == 'docker':
        file_path = path.join(module_path, 'models/dockerignore.txt')
        file_text = open(file_path).read()

    return file_text

def merge_ignores(standard_text, insert_text):

    ''' a method to upsert one ignore text into another '''
    
# define regex patterns
    import re
    section_regex = re.compile('\n(#+\s+.*?\s+#+\n.*?)(?=$|\n#)', re.S)
    header_regex = re.compile('#+\s+(.*?)\s+#+')
    title_line = insert_text.splitlines()[0]
    title_pattern = '#+\s+%s\s+#+' % (header_regex.findall(title_line)[0])
    title_regex = re.compile(title_pattern)
    newline_regex = re.compile('\n{3,}', re.S)

# retrieve sections and lines
    insert_sections = section_regex.findall(insert_text)
    standard_lines = standard_text.splitlines()

    extra_lines = []
    
# insert lines into standard text
    for section in insert_sections:
        section_lines = section.splitlines()
        header_line = section_lines[0]
        header_name = header_regex.findall(header_line)[0]
        add_list = []
        for i in range(1,len(section_lines)):
            if not section_lines[i] in standard_lines:
                add_list.append(section_lines[i])
        section_exists = False
        if standard_lines:
            for i in range(len(standard_lines)):
                header_results = header_regex.findall(standard_lines[i])
                if header_results:
                    if header_results[0] == header_name:
                        index = i + 1
                        add_list = sorted(add_list, reverse=True)
                        for j in range(len(add_list)):
                            standard_lines.insert(index, add_list[j])
                        section_exists = True
                        break
# add non-existent sections to extra lines
        if not section_exists:
            if len(section_lines) > 1:
                if add_list or not(section_lines[1]):
                    if not extra_lines:
                        extra_lines.extend(['',''])
                    extra_lines.append(header_line)
                    extra_lines.extend(add_list)
                    extra_lines.append('')

# rejoin text
    merged_text = ''
    if standard_lines:
        if not title_regex.findall(standard_lines[0]):
            merged_text = '\n'.join([ title_line, '', ''])
    merged_text += '\n'.join(standard_lines)
    merged_text = merged_text.strip()
    merged_text += '\n'.join(extra_lines)

# remove extra lines
    merged_text = newline_regex.sub('\n\n', merged_text)

    return merged_text

if __name__ == '__main__':
    test_ignore = '../../tests/.testgitignore'
    ignore_text = open(test_ignore).read()
    insert_text = load_ignore()
    merged_text = merge_ignores(ignore_text, insert_text)
    print(merged_text)
