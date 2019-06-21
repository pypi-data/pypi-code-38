import delivery


def test_basic_notification():
    delivery.notify(
        "This Is A Title", "This notification should have a title and a message."
    )


def test_no_title():
    assert_raises(
        ValueError,
        delivery.notify,
        title="",
        message="This notification just has a message",
    )
