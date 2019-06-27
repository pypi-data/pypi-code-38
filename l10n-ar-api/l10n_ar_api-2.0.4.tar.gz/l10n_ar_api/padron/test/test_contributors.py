from l10n_ar_api.padron.contributor import Contributor


class TestContribuyentes:

    def test_valid_cuit(self):
        cuit = '30709653543'
        assert Contributor.is_valid_cuit(cuit)
        cuit = 30709653543
        assert Contributor.is_valid_cuit(cuit)

    def test_invalid_cuit(self):
        cuit = '30709653542'
        assert Contributor.is_valid_cuit(cuit) == 0
        cuit = 30709653542
        assert Contributor.is_valid_cuit(cuit) == 0

    def test_cuit_without_11_digits(self):
        cuit = '3070965354'
        assert Contributor.is_valid_cuit(cuit) == 0
        cuit = 3070965354
        assert Contributor.is_valid_cuit(cuit) == 0

    def test_11_digits_no_int(self):
        cuit = 'A1234567891'
        assert Contributor.is_valid_cuit(cuit) == 0

    def test_cuit_with_dash(self):
        cuit = '30-70965354-3'
        assert Contributor.is_valid_cuit(cuit) == 0
