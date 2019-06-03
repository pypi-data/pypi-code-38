#!/home/dd/anaconda3/bin/python
import re
import requests

def main(url, omm_function):

    def parse_yno_file_readlines(content):
        """parse .omm readlines list for yotas spanning 
        several lines, return list of yota strings."""

        parsed_lines = []
        for line in content:
                line = line.strip()
                if len(line) > 2:  # filter empty lines
                    m0 = re.search('^#', line)
                    if not m0: # filter comments
                        m = re.search('^\.', line)
                        if m: # concatinate multiple line yotas
                            parsed_lines[-1] += line
                        else:
                            parsed_lines.append(line)
        return(parsed_lines)

    # with open(filename) as f:
    #     filelines = f.readlines()

    r = requests.get(url)
    file_content = r.text.split("\n")
    #print(f'file_content: {file_content}')

    filelines2 = parse_yno_file_readlines(file_content)
    omm = omm_function

    if len(filelines2) > 1:
        mixtape = omm(filelines2[0]) + omm(filelines2[1])
    else:
        mixtape = omm(filelines2[0])

    for line in filelines2[2:]:
        mixtape += omm(line)

    return(mixtape)

