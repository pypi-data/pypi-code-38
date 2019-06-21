import os
import subprocess,re
from datetime import datetime

FIREFOX = r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{0}.{1}) Gecko/20100101 Firefox/{0}.{1}"
VERSION = re.compile(r'(\d+)\.(\d+)\.(\d+)')
DATE = re.compile(r'DATE_CHECKED\s+=\s+"(.*?)"', re.MULTILINE|re.DOTALL)
CDEF = re.compile(r'DEFAULT\s*=\s*"\d+\.\d+"', re.MULTILINE|re.DOTALL)
DAYS_BEFORE_CHECK = 30
DATE_CHECKED = "2019-05-15"  # Don't change manually
DEFAULT = "66.0"  # Don't change manually


def timediff():
    date_format = "%Y-%m-%d"
    last_date = datetime.strptime(DATE_CHECKED, date_format)
    today = datetime.strptime(datetime.now().strftime(date_format), date_format)
    days = abs(today - last_date).days
    if days >= DAYS_BEFORE_CHECK:
        return True
    else:
        return False


def get():
    if timediff():
        py_loc = os.path.abspath(__file__)
        with open(py_loc) as f:
            program_data = f.read()
            date_format = "%Y-%m-%d"
            rebuild1 = re.sub(DATE.search(program_data).group(1), str(datetime.now().strftime(date_format)),
                              program_data)
            try:
                x = subprocess.check_output([FIREFOX, '-v', "|", "more"])
                version_no = x.strip()
                try:
                    a, b, c = VERSION.search(version_no.decode()).groups()
                except:
                    raise FileNotFoundError("Check firefox path")

                rebuild2 = CDEF.sub('DEFAULT = "{0}.{1}"'.format(a, b), rebuild1)
                with open(py_loc, "w") as f:
                    f.write(rebuild2)
            except:
                "failed to access firefox returned non-zero"

    return USER_AGENT.format(*DEFAULT.split("."))
