import os.path
import sys


# Enable running edit with edit in a non-standard location.
# This was once used to run development versions of edit.
# Because PEP 434 declared edit.py a public interface,
# removal should require deprecation.
edit_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if edit_dir not in sys.path:
    sys.path.insert(0, edit_dir)

from edit.pyshell import main  # This is subject to change
main()
