import sys

import datetime
import psycopg2
from tqdm import tqdm
from xml.etree.ElementTree import tostring, fromstring as fromstring_xml

from ucca import convert
from ucca.ioutil import external_write_mode

UNK_LINKAGE_TYPE = 'UNK'
CONNECTION = None


def fromstring(text):
    text = text.replace(r"\u2019", "&apos;")
    text = text.replace(r"\u2013", "-")
    text = text.replace(r"\u2014", "-")
    text = text.replace(r"\u2032", "'")
    text = text.replace(r"\u201C", '"')
    text = text.replace(r"\u201D", '"')
    if r"\u" in text:
        raise Exception("Unescaped unicode: " + text)
    return fromstring_xml(text)


#######################################################################################
# Returns the most recent xmls from db with a passage id pid and usernames
# (a list). The xmls are ordered in the same way as the list usernames.
#######################################################################################
def get_xmls_by_username(host_name, db_name, username):
    c = get_cursor(host_name, db_name)
    uid = get_uid(host_name, db_name, username)
    c.execute("SELECT xml FROM xmls WHERE uid=%s AND ts IN (SELECT MAX(ts) from xmls GROUP BY paid)", (uid,))
    for queryset in c.fetchall():
        yield fromstring(queryset[0])


def get_xml_trees(host_name, db_name, pid, usernames=None, graceful=False):
    """ Params: db, host, paragraph id, the list of usernames wanted,
        Optional:
        graceful: True if no excpetions are to be raised
        excpetion raised if a user did not submit an annotation for the passage
        returns a list of xml roots elements
        """
    c = get_cursor(host_name, db_name)
    xmls = []
    if usernames is None:
        c.execute("SELECT xml FROM xmls WHERE paid=%s ORDER BY ts DESC", (pid,))
        queryset = c.fetchone()
        if queryset is not None:
            xmls.append(fromstring(queryset[0]))
    else:
        for username in usernames:
            username = str(username)  # precaution for cases bad input e.g. 101
            cur_uid = get_uid(host_name, db_name, username)
            c.execute("SELECT xml FROM xmls WHERE paid=%s AND uid=%s ORDER BY ts DESC", (pid, cur_uid))
            raw_xml = c.fetchone()
            if not raw_xml and not graceful:
                raise Exception("The user " + username +
                                " did not submit an annotation for this passage")
            else:
                xmls.append(fromstring(raw_xml[0]))
    return xmls


def get_by_xids(host_name, db_name, xids, **kwargs):
    """Returns the passages that correspond to xids (which is a list of them)"""
    del kwargs
    c = get_cursor(host_name, db_name)
    xmls = []
    for xid in xids:
        c.execute("SELECT xml FROM xmls WHERE id=%s", (int(xid),))
        queryset = c.fetchone()
        if queryset is None:
            raise Exception("The xid " + xid + " does not exist")
        else:
            xmls.append(fromstring(queryset[0]))
    return xmls


def get_most_recent_passage_by_uid(uid, passage_id, host_name, db_name, verbose=False, write_xids=None, strict=False,
                                   **kwargs):
    del kwargs
    c = get_cursor(host_name, db_name)
    uid = (uid,) if isinstance(uid, (str, int)) else tuple(uid)
    if "*" in uid:
        c.execute("SELECT xml,status,ts,id,uid FROM xmls WHERE paid = %s ORDER BY ts DESC", (passage_id,))
    else:
        c.execute("SELECT xml,status,ts,id,uid FROM xmls WHERE uid IN %s AND paid = %s ORDER BY ts DESC",
                  (uid, passage_id))
    queryset = c.fetchone()
    raw_xml, status, ts, xid, uid = 5 * [None]
    if queryset is None:
        if strict:
            raise Exception("The user %s did not annotate passage %s" % (uid, passage_id))
    else:
        raw_xml, status, ts, xid, uid = queryset
    if write_xids:
        with open(write_xids, "a") as f:
            print(passage_id, xid, uid, ts, file=f, sep="\t")
    if queryset is None:
        return None
    if int(status) != 1:  # if not submitted
        with external_write_mode():
            print("The most recent xml for uid %s and paid %s is not submitted." % (uid, passage_id), file=sys.stderr)
    if verbose:
        with external_write_mode():
            print("Timestamp: %s, uid: %d, xid: %d" % (ts, uid, xid))
    return fromstring(raw_xml)


def get_uid(host_name, db_name, username):
    """Returns the uid matching the given username."""
    c = get_cursor(host_name, db_name)
    c.execute("SELECT id FROM users WHERE username=%s", (username,))
    cur_uid = c.fetchone()
    if cur_uid is None:
        raise Exception("The user " + username + " does not exist")
    return int(cur_uid[0])


def write_to_db(host_name, db_name, xml, new_pid, new_prid, username, status=1):
    con = get_connection(db_name, host_name)
    c = con.cursor()
    c.execute("SET search_path TO oabend")

    c.execute("SELECT id FROM users WHERE username=%s", (username,))
    cur_uid = c.fetchone()
    if cur_uid is None:
        raise Exception("The user " + username + " does not exist")
    else:
        cur_uid = cur_uid[0]
    now = datetime.datetime.now()
    c.execute("INSERT INTO xmls (reviewOf, xml, paid, prid, uid, comment, status, ts) "
              "VALUES (-1, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
              (xml, new_pid, new_prid, cur_uid, '', status, now))
    queryset = c.fetchone()
    con.commit()
    return None if queryset is None else queryset[0]


def get_most_recent_xids(host_name, db_name, username):
    """Returns the most recent xids of the given username."""
    cur_uid = get_uid(host_name, db_name, username)
    c = get_cursor(host_name, db_name)
    c.execute("SELECT id, paid FROM xmls WHERE uid=%s ORDER BY ts DESC", (cur_uid,))
    print(username)
    print("=============")
    r = c.fetchone()
    count = 0
    while r and count < 10:
        print(r)
        r = c.fetchone()
        count += 1


def get_passage(host_name, db_name, pid):
    """Returns the passages with the given id numbers"""
    c = get_cursor(host_name, db_name)
    c.execute("SELECT passage FROM passages WHERE id=%s", (pid,))
    queryset = c.fetchone()
    if queryset is None:
        raise Exception("No passage with ID=" + pid)
    return queryset[0]


def linkage_type(u):
    """
    Returns the type of the primary linkage the scene participates in.
    It can be A,E or H. if it is a C, it returns the taf of the first fparent which is an A,E or H.
    If it does not find an fparent with either of these categories, it returns UNK_LINKAGE_TYPE.
    """
    cur_u = u
    while cur_u is not None:
        if cur_u.ftag in ['A', 'E', 'H']:
            return cur_u.ftag
        elif cur_u.ftag != 'C':
            return UNK_LINKAGE_TYPE
        else:
            cur_u = cur_u.fparent
    return UNK_LINKAGE_TYPE


def unit_length(u):
    """
    Returns the number of terminals (excluding remote units and punctuations) that are descendants of the unit u.
    """
    return len(u.get_terminals(punct=False, remotes=False))


def print_passages_to_file(host_name, db_name, paids, write_xml=False, write_site_xml=False, prefix='', start_index=0):
    """
    Returns for that user a list of submitted passages and a list of assigned but not submitted passages.
    Each passage is given in the format: (<passage ID>, <source>, <recent submitted xid or -1 if not submitted>,
    <number of tokens in the passage>, <number of units in the passage>, <number of scenes in the passage>,
    <average length of a scene>). It also returns a distribution of the categories.
    write_xml: determines whether to write it to a file, named <prefix><the number of the xml>.xml
    skip_first: the index of the passage where it should start looking (the ones before are skipped)
    """
    c = get_cursor(host_name, db_name)

    for paid in paids:
        if paid < start_index:  # skipping training passages
            continue
        c.execute("SELECT passage,source FROM passages WHERE id=%s", (paid,))
        r = c.fetchone()
        if r is not None:
            source = r[1]
            c.execute("SELECT id, xml,uid,ts FROM xmls WHERE paid=%s ORDER BY ts DESC", (paid,))
            r = c.fetchone()
            if r is not None:
                xid = r[0]
                uid = r[2]
                ts = r[3]
                print('\t'.join([str(paid), str(uid), str(source), str(xid), str(ts)]))

                if write_site_xml:
                    f = open(prefix + str(paid) + '_site.xml', 'w', encoding='utf-8')
                    f.write(r[1] + '\n')
                    f.close()
                # noinspection PyBroadException
                try:
                    ucca_dag = convert.from_site(fromstring(r[1]))
                except Exception:
                    sys.stderr.write("Skipped xid,paid " + str((xid, paid)) + "\n")
                    continue
                if write_xml:
                    f = open(prefix + str(paid) + '.xml', 'w')
                    f.write(tostring(convert.to_standard(ucca_dag)).decode())
                    f.close()


def get_predicates(host_name, db_name, only_complex=True):
    """
    Returns a list of all the predicates in the UCCA corpus.
    usernames -- the names of the users whose completed passages we should take.
    only_complex -- only the multi-word predicates will be returned.
    start_index -- the minimal passage number to be taken into account.
    """
    def _complex(u):
        """ Returns True if u is complex, i.e., if it has more than one child which is not an F or punct """
        if u is None or u.tag != 'FN':
            return False
        non_function_count = 0
        non_function_u = None
        for e in u.outgoing:
            if e.child.tag == 'FN' and e.tag != 'F':
                non_function_count += 1
                non_function_u = e.child
        return True if non_function_count > 1 else _complex(non_function_u)

    c = get_cursor(host_name, db_name)
    # uid = get_uid(host_name, db_name, username)
    # get all the completed xmls
    c.execute("SELECT id, xml FROM xmls WHERE status=%s AND reviewOf<>%s ORDER BY ts DESC", (1, -1))
    predicates = c.fetchall()

    with open('preds', 'w') as f:
        for r in tqdm(predicates):
            # noinspection PyBroadException
            try:
                ucca_dag = convert.from_site(fromstring(r[1]))
            except Exception:
                print("Skipped.", file=sys.stderr)
                continue

            # gathering statistics
            scenes = [x for x in ucca_dag.layer("1").all if x.tag == "FN" and x.is_scene()]
            for sc in scenes:
                main_relation = sc.process if sc.process is not None else sc.state
                if only_complex and not _complex(main_relation):
                    continue
                try:
                    print(main_relation.to_text(), file=f)
                except UnicodeEncodeError:
                    print("Skipped (encoding issue).", file=sys.stderr)
                    continue


def get_cursor(host_name, db_name):
    """ create a cursor to the search path """
    con = get_connection(db_name, host_name)
    c = con.cursor()
    c.execute("SET search_path TO oabend")
    return c


def get_connection(db_name, host_name):
    """ connects to the db and host, returns a connection object """
    global CONNECTION
    CONNECTION = psycopg2.connect(host=host_name, database=db_name)
    return CONNECTION


def main(argv):
    t = tqdm(globals()[argv[1]]("pgserver", "work", *argv[2:]), unit=" passages", desc="Downloading XMLs")
    for xml in t:
        p = convert.from_site(xml)
        t.set_postfix(ID=p.ID)
        convert.passage2file(p, p.ID + ".xml")


if __name__ == "__main__":
    main(sys.argv)
