
from j5basic import CleanXHTML
import six

DIRTY_XHTML = """
Testing fragment<br/>
<span id="this_is_a_great_id" class="MYCLASS" style="badstyle" lang="en-inve-us">TEXT</span>
<span/>
"""

def test_clean_html():
    cleaned_html = CleanXHTML.clean_html(six.text_type(DIRTY_XHTML))
    assert cleaned_html == six.text_type("\nTesting fragment<br/>\nTEXT\n\n")