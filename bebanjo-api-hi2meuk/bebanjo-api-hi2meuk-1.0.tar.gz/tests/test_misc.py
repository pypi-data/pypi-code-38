from bebanjo.things import overlay_url, name_from_resource
from bebanjo.utils import rm_csv_tag, add_csv_tag


def test_overlay_url():
    cases = [
        ('http://localhost:8080/api', '/images', 'http://localhost:8080/api/images'),
        ('http://localhost:8080/api', 'images', 'http://localhost:8080/api/images'),
        ('http://localhost:8080/api', 'schedule', 'http://localhost:8080/api/schedule'),
        ('http://localhost:8080/api/tiles/1001', 'images',
         'http://localhost:8080/api/tiles/1001/images'),
        ('http://localhost:8080/api/events', 'http://localhost:8080/api/images/5001',
         'http://localhost:8080/api/images/5001'),
    ]
    for left, right, result in cases:
        assert overlay_url(left, right) == result


def test_name_from_resource():
    cases = [
        ('http://localhost:8080/api/title/schedule', 'schedule'),
        ('http://localhost:8080/api/title/schedule/schedulings', 'schedulings'),
        ('http://localhost:8080/api/title/schedule/schedulings/3647', 'schedulings'),
        ('http://localhost:8080/api/assets/123/target_platforms/874', 'target_platforms'),
    ]
    for url, result in cases:
        assert name_from_resource(url) == result


def test_rm_csv_tag():
    cases = (
        ('fred,JOHN,Harry', 'fred', 'JOHN,Harry'),
        ('fred,JOHN,Harry', 'JOHN', 'fred,Harry'),
        ('fred,JOHN,Harry', 'Harry', 'fred,JOHN'),
    )
    for tags, rm, result in cases:
        assert rm_csv_tag(tags, rm) == result


def test_add_csv_tag():
    cases = [
        ('a,b,c', 'h'),
        ('a,b,b,c', 'h'),
    ]
    for tags, new in cases:
        new_tags = add_csv_tag(tags, new)
        assert len(new_tags) == 7
