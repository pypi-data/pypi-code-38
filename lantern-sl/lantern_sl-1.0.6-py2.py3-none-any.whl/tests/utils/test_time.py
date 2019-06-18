from lantern_sl.utils.time import current_ts

def test_current_ts():
    ts = current_ts()
    assert len(str(ts)) == 13, "timestamp has 13 size"
