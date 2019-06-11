# =============================================================================
# Copyright [2018] [Miguel Alex Cantu]
# License Information :
# This software has no warranty, it is provided 'as is'. It is your
# responsibility to validate the behavior of the routines and its accuracy
# using the code provided. Consult the GNU General Public license for further
# details (see GNU General Public License).
# http://www.gnu.org/licenses/gpl.html
# =============================================================================
import re
from priscillaandaquila import args
from diyr.utils.bible import Bible
import pdb

def main():
    """
    This is a command line utility and takes in a comma delimited list of
    verse references, performs a lookup on each reference, and returns a
    list of their corresponding verses
    """
    parsed_args = args.get_parser().parse_args()
    bible = Bible()
    if parsed_args.file:
        verse_refs = open(parsed_args.file, 'r')
    elif parsed_args.verses:
        verse_refs = parsed_args.verses.split(';')
    else:
        raise Exception("Choose an argument!")
    for verse_ref in verse_refs:
        # Verses in the same book can be subsequently listed without the
        # the book name. This is handled seperately by _expand_verse_range
        # by considering first the reference with the book name, then any
        # verses that may be listed.
        _ = verse_ref.split(',')
        verse_ref = _[0]
        listed_verses = _[1:]
        # Expand the verse reference, so that users can also
        # provide book abbrivations.
        extrapolated_verse_ref = bible.extrapolate_abbriv(verse_ref.strip(),
                                                          raise_exp = False)
        # Splitting verse to book, chapter, verse(s)
        reg = re.compile('(([0-9] )*[a-zA-Z]*) *([0-9]*:)*([0-9]*-*[0-9]*)')
        _verse_refs = _expand_verse_range(reg,
                                          extrapolated_verse_ref,
                                          listed_verses)

        for _verse_ref in _verse_refs:
            m = reg.match(_verse_ref)
            verse = bible.verse_lookup(m.group(1).strip(),
                                       m.group(3).strip().replace(":",""),
                                       m.group(4).strip())
            # Strip off identifier returned by "verse_lookup"
            verse = re.sub('[0-9]*\.', '', verse).strip()

            if parsed_args.references_first:
                print "{} {}:{} - {}".format(
                    m.group(1).strip(),
                    m.group(3).strip().replace(":",""),
                    m.group(4).strip(),
                    verse)
            else:
                print "{} - {} {}:{}".format(
                    verse,
                    m.group(1).strip(),
                    m.group(3).strip().replace(":", ""),
                    m.group(4).strip())

def _expand_verse_range(reg, verse_ref, listed_verses):
    """
    Takes in a Reg  object with very specific groupings. The
    groupings must follow these specifications:
    group(0) - The matched string
    group(1) - The book name
    group(2) - The book number
    group(3) - The book chapter
    group(4) - The verse, or a verse range to be expanded.
    If group(4) is just a single verse, then this method will
    not attempt any logic. If group(4) is a verse range, i.e.
    1 Corin. 2:11-14, the method will return a list of all the
    verses in that range, inclusively.

    The second argument is the verse reference to be expanded.

    The third argument is a list of verses, without book reference, whose
    book name will be the same as the one used for ``verse_ref``
    """
    verses_expanded = []
    # Get the book name and chapter of verse_ref, might be used
    # later to deduce the full reference in listed_verses
    m = reg.match(verse_ref)
    book_name = m.group(1).strip()
    chapter = m.group(3).strip().replace(":","")

    for verses in [verse_ref] + listed_verses:
        m = reg.match(verses.strip())


        # If ":" exist in the string, that indicates a new chapter is being
        # referenced.
        if ":" in verses:
            chapter = m.group(3).replace(":","")

        # If "-" exist in the string, that indicates a range of verses that
        # needs to be expanded.
        if "-" in m.group(4):
            verse_ends = m.group(4).split('-')
            for i in xrange(int(verse_ends[0]), int(verse_ends[1]) + 1):
                verses_expanded.append("{} {}:{}".format(
                    book_name,
                    chapter,
                    str(i)))
        else:
            verses_expanded.append("{} {}:{}".format(
                book_name,
                chapter,
                m.group(4).strip()))

    return verses_expanded


if __name__ == '__main__':
    main()
