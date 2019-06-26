from django import test

from ievv_opensource.ievv_sms.phone_number_handler import NorwegianPhoneNumberHandler


class TestNorwegianPhoneNumberHandler(test.TestCase):
    def test_get_country_calling_code_starts_with_00(self):
        self.assertEqual(NorwegianPhoneNumberHandler('004712345678').get_country_calling_code(), 47)
        self.assertEqual(NorwegianPhoneNumberHandler('00 47 12 34 56 78').get_country_calling_code(), 47)
        self.assertIsNone(NorwegianPhoneNumberHandler('0047123456789').get_country_calling_code())
        self.assertIsNone(NorwegianPhoneNumberHandler('00471234567').get_country_calling_code())
        self.assertIsNone(NorwegianPhoneNumberHandler('004812345678').get_country_calling_code())

    def test_get_country_calling_code_starts_with_plus(self):
        self.assertEqual(NorwegianPhoneNumberHandler('+4712345678').get_country_calling_code(), 47)
        self.assertEqual(NorwegianPhoneNumberHandler('+ 47 12 34 56 78').get_country_calling_code(), 47)
        self.assertIsNone(NorwegianPhoneNumberHandler('+47123456789').get_country_calling_code())
        self.assertIsNone(NorwegianPhoneNumberHandler('+471234567').get_country_calling_code())
        self.assertIsNone(NorwegianPhoneNumberHandler('+4812345678').get_country_calling_code())

    def test_get_country_calling_code_no_code(self):
        self.assertEqual(NorwegianPhoneNumberHandler('12345678').get_country_calling_code(), 47)
        self.assertEqual(NorwegianPhoneNumberHandler('12 34 56 78').get_country_calling_code(), 47)
        self.assertIsNone(NorwegianPhoneNumberHandler('123456789').get_country_calling_code())
        self.assertIsNone(NorwegianPhoneNumberHandler('1234567').get_country_calling_code())

    def test_get_phone_number_without_country_code_starts_with_00(self):
        self.assertEqual(NorwegianPhoneNumberHandler('004712345678').get_phone_number_without_country_code(),
                         '12345678')
        self.assertEqual(NorwegianPhoneNumberHandler('00 47 12 34 56 78').get_phone_number_without_country_code(),
                         '12345678')
        self.assertIsNone(NorwegianPhoneNumberHandler('0047123456789').get_phone_number_without_country_code(),
                          '0047123456789')
        self.assertIsNone(NorwegianPhoneNumberHandler('00471234567').get_phone_number_without_country_code(),
                          '00471234567')
        self.assertIsNone(NorwegianPhoneNumberHandler('004812345678').get_phone_number_without_country_code(),
                          '004812345678')

    def test_get_phone_number_without_country_code_starts_with_plus(self):
        self.assertEqual(NorwegianPhoneNumberHandler('+4712345678').get_phone_number_without_country_code(),
                         '12345678')
        self.assertEqual(NorwegianPhoneNumberHandler('+ 47 12 34 56 78').get_phone_number_without_country_code(),
                         '12345678')
        self.assertIsNone(NorwegianPhoneNumberHandler('+47123456789').get_phone_number_without_country_code(),
                          '+47123456789')
        self.assertIsNone(NorwegianPhoneNumberHandler('+471234567').get_phone_number_without_country_code(),
                          '+471234567')
        self.assertIsNone(NorwegianPhoneNumberHandler('+4812345678').get_phone_number_without_country_code(),
                          '+4812345678')

    def test_get_phone_number_without_country_code_no_code(self):
        self.assertEqual(NorwegianPhoneNumberHandler('12345678').get_phone_number_without_country_code(),
                         '12345678')
        self.assertEqual(NorwegianPhoneNumberHandler('12 34 56 78').get_phone_number_without_country_code(),
                         '12345678')
        self.assertIsNone(NorwegianPhoneNumberHandler('123456789').get_phone_number_without_country_code(),
                          '123456789')
        self.assertIsNone(NorwegianPhoneNumberHandler('1234567').get_phone_number_without_country_code(),
                          '1234567')

    def test_can_receive_sms_starts_with_00(self):
        self.assertTrue(NorwegianPhoneNumberHandler('004792345678').can_receive_sms())
        self.assertTrue(NorwegianPhoneNumberHandler('00 47 92 34 56 78').can_receive_sms())
        self.assertFalse(NorwegianPhoneNumberHandler('004712345678').can_receive_sms())
        self.assertFalse(NorwegianPhoneNumberHandler('0047923456789').can_receive_sms())
        self.assertFalse(NorwegianPhoneNumberHandler('00479234567').can_receive_sms())
        self.assertFalse(NorwegianPhoneNumberHandler('004892345678').can_receive_sms())

    def test_can_receive_sms_starts_with_plus(self):
        self.assertTrue(NorwegianPhoneNumberHandler('+4792345678').can_receive_sms())
        self.assertTrue(NorwegianPhoneNumberHandler('+ 47 92 34 56 78').can_receive_sms())
        self.assertFalse(NorwegianPhoneNumberHandler('+4712345678').can_receive_sms())
        self.assertFalse(NorwegianPhoneNumberHandler('+47923456789').can_receive_sms())
        self.assertFalse(NorwegianPhoneNumberHandler('+479234567').can_receive_sms())
        self.assertFalse(NorwegianPhoneNumberHandler('+4892345678').can_receive_sms())

    def test_can_receive_sms_no_code(self):
        self.assertTrue(NorwegianPhoneNumberHandler('92345678').can_receive_sms())
        self.assertTrue(NorwegianPhoneNumberHandler('92 34 56 78').can_receive_sms())
        self.assertFalse(NorwegianPhoneNumberHandler('12345678').can_receive_sms())
        self.assertFalse(NorwegianPhoneNumberHandler('923456789').can_receive_sms())
        self.assertFalse(NorwegianPhoneNumberHandler('9234567').can_receive_sms())

    def test_cleaned_phone_number(self):
        self.assertEqual(NorwegianPhoneNumberHandler('004712345678').get_cleaned_phone_number(),
                         '+4712345678')
        self.assertEqual(NorwegianPhoneNumberHandler('+4712345678').get_cleaned_phone_number(),
                         '+4712345678')
        self.assertEqual(NorwegianPhoneNumberHandler('00 47 12 34 56 78').get_cleaned_phone_number(),
                         '+4712345678')
        self.assertEqual(NorwegianPhoneNumberHandler('+47 12 34 56 78').get_cleaned_phone_number(),
                         '+4712345678')
        self.assertEqual(NorwegianPhoneNumberHandler('12345678').get_cleaned_phone_number(),
                         '+4712345678')
        self.assertEqual(NorwegianPhoneNumberHandler('12 34 56 78').get_cleaned_phone_number(),
                         '+4712345678')
        self.assertIsNone(NorwegianPhoneNumberHandler('004812345678').get_cleaned_phone_number())
        self.assertIsNone(NorwegianPhoneNumberHandler('+4882345678').get_cleaned_phone_number())
        self.assertIsNone(NorwegianPhoneNumberHandler('0047123456789').get_cleaned_phone_number())
        self.assertIsNone(NorwegianPhoneNumberHandler('00471234567').get_cleaned_phone_number())

    def test_get_normalized_phone_number(self):
        self.assertEqual(NorwegianPhoneNumberHandler('004712345678').get_normalized_phone_number(),
                         '+4712345678')
        self.assertEqual(NorwegianPhoneNumberHandler('+4712345678').get_normalized_phone_number(),
                         '+4712345678')
        self.assertEqual(NorwegianPhoneNumberHandler('00 47 12 34 56 78').get_normalized_phone_number(),
                         '+4712345678')
        self.assertEqual(NorwegianPhoneNumberHandler('+47 12 34 56 78').get_normalized_phone_number(),
                         '+4712345678')
        self.assertEqual(NorwegianPhoneNumberHandler('12345678').get_normalized_phone_number(),
                         '+4712345678')
        self.assertEqual(NorwegianPhoneNumberHandler('12 34 56 78').get_normalized_phone_number(),
                         '+4712345678')

        self.assertEqual(NorwegianPhoneNumberHandler('004812345678').get_normalized_phone_number(), '004812345678')
        self.assertEqual(NorwegianPhoneNumberHandler('+4882345678').get_normalized_phone_number(), '+4882345678')
        self.assertEqual(NorwegianPhoneNumberHandler('0047123456789').get_normalized_phone_number(), '0047123456789')
        self.assertEqual(NorwegianPhoneNumberHandler('00471234567').get_normalized_phone_number(), '00471234567')

        self.assertEqual(NorwegianPhoneNumberHandler('0048 123 45 678').get_normalized_phone_number(), '004812345678')
        self.assertEqual(NorwegianPhoneNumberHandler('+488 2345 678').get_normalized_phone_number(), '+4882345678')
        self.assertEqual(NorwegianPhoneNumberHandler('00471 2  345  6789').get_normalized_phone_number(),
                         '0047123456789')
        self.assertEqual(NorwegianPhoneNumberHandler('004  712 34567').get_normalized_phone_number(), '00471234567')
