from django_vox import base


def test_domain():
    site = base.get_current_site()
    assert "127.0.0.1:8000" == site.domain
    assert "127.0.0.1:8000" == str(site)


def test_full_iri():
    data = (
        ("http://127.0.0.1:8000/foo/bar", "/foo/bar"),
        ("http://foo/bar", "//foo/bar"),
        ("http://bar", "http://bar"),
    )
    for expected, url in data:
        assert expected == base.full_iri(url)


def test_contact():
    contact = base.Contact("John Doe", "email", "john@doe.name")
    assert "John Doe <email:john@doe.name>" == str(contact)
    assert hash(("John Doe", "email", "john@doe.name")) == hash(contact)
