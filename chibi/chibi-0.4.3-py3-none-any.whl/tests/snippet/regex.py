from unittest import TestCase

from chibi.snippet import regex


class test_regex(TestCase):

    def setUp(self):
        self.valid_email = [
            '"abcdefghixyz"@example1.com', 'abc."defghi".xyz@example-1.com',
            'niceandsimple@example.com', 'very.common@example.com',
            'a.little.lengthy.but.fine@dept.example.com',
            'disposable.style.email.with+symbol@example.com',
            'other.email-with-dash@example.com',
            '"much.more unusual"@example.com',
            '"very.unusual.@.unusual.com"@example.com',
            ('"very.(),:;<>[]\\".VERY.\\"very@\\ \\"very\\".unusual"'
             '@strange.example.com' ),
            'admin@mailserver1', '#!$%&\'*+-/=?^_`{}|~@example.org',
            '"()<>[]:,;@\\\"!#$%&\'*+-/=?^_`{}| ~.a"@example.org',
            '" "@example.org', 'jsmith@example.org', 'jsmith@[192.168.2.1]',
        ]

        self.invalid_email = [
            'abc\"def\"ghi@example.com', 'abc"defghi"xyz@example.com',
            'Abc.example.com', 'A@b@c@example.com',
            'a"b(c)d,e:f;g<h>i[j\k]l@example.com',
            'just"not"right@example.com',
            'this is"not\allowed@example.com',
            'this\ still\"not\\allowed@example.com',
            'john..doe@example.com', 'john.doe@example..com', ]

    def test_test(self):
        re = r'10*1'
        inner = 0
        s = '1%s1'

        for i in range(10):
            regex.test(re, s % (inner * i))

    def test_email_validate(self):
        for email in self.valid_email:
            self.assertTrue(
                regex.is_email( email ),
                "this is a valid email: {}".format( email ) )

    def test_email_validate_with_invalid(self):
        for email in self.invalid_email:
            self.assertFalse(
                regex.is_email( email ),
                "this is a invalid email: {}".format( email ) )
