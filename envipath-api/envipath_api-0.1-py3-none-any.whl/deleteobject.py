#!/usr/bin/python
"""
Created on Mon Jun 13 13:18:08 2016

@author: me
"""

from envirest import commonparser, login, logout


def confirm(message):
    question = "{}\nok? [y/N] ".format(message)
    answer = raw_input(question)
    return answer.lower() == 'y'


def deleteobject(session, objecturl, verify=True, forced=False):

    headers={"Accept": "application/json"}
    if forced or confirm("delete object {}".format(objecturl)):
        r = session.delete(objecturl, headers=headers, allow_redirects=True, verify=verify)
    else:
        r = 'deletion not confirmed'
    return r


def main():
    parser = commonparser(prog='deleteobject', description='delete an object from enviPath')
    parser.add_argument('objecturl', action='store',
                        help='the object to be deleted')
    parser.add_argument('--forced', dest='forced', action='store',
                        help='force deletion without confirmation')
    args = parser.parse_args()

    session = login(hosturl=args.host, username=args.user, password=args.password, verify=args.verify)
    try:
        returned = deleteobject(session, objecturl=args.objecturl, verify=args.verify, forced=(args.forced=='true'))
    finally:
        logout(session, hosturl=args.host, verify=args.verify)
    print(returned, '.')


if __name__ == "__main__":
    main()
