import timestamp_finder


def test_valid_date_text():
    result = timestamp_finder.date_text_to_filename("2013:12:01 13:23:12")
    assert result is not None


def test_empty_date_text():
    result = timestamp_finder.date_text_to_filename(": :    :    :")
    assert result is None


def test_exif_version_0220():
    result = timestamp_finder.get_timestamp("tests/test_data/0220.jpg")
    assert result == "20070802_123020"


def test_exif_version_0221():
    result = timestamp_finder.get_timestamp("tests/test_data/0221.jpg")
    assert result == "20150704_172516"


def test_invalid_file():
    result = timestamp_finder.get_timestamp("tests/test_data/foo.jpg")
    assert result is None
