import pytest

from xoinvader.vector import Vec2, Vec3


def test_point_operations():
    ax, ay, az = 10, 10, 10
    bx, by, bz = 20, 20, 20
    a = Vec3(ax, ay, az)
    b = Vec3(bx, by, bz)

    assert a.x == ax
    assert a.y == ay
    assert a.z == az
    assert b.x == bx
    assert b.y == by
    assert b.z == bz

    assert repr(a) == "Vec3(x={0}, y={1}, z={2})".format(
        a.x, a.y, a.z)

    assert a + b == Vec3(ax + bx, ay + by, az + bz)
    assert a - b == Vec3(ax - bx, ay - by, az - bz)
    assert a + 5 == Vec3(ax + 5, ay + 5, az + 5)
    assert a - 5 == Vec3(ax - 5, ay - 5, az - 5)
    assert a * 5 == Vec3(ax * 5, ay * 5, az * 5)
    assert a / 5 == Vec3(ax / 5, ay / 5, az / 5)

    with pytest.raises(ValueError):
        assert a + "a"
    with pytest.raises(ValueError):
        assert a - "a"
    with pytest.raises(ValueError):
        assert a * "a"
    with pytest.raises(ValueError):
        assert a / "a"
    with pytest.raises(ValueError):
        assert a == "a"

    a.x = bx
    a.y = by
    a.z = bz

    assert a.x == bx
    assert a.y == by
    assert a.z == bz

    b.x = -bx
    b.y = -by
    b.z = -bz

    assert a + b == Vec3(0, 0, 0)
    assert a + Vec3(-50, -50, -50) == Vec3(-30, -30, -30)

    assert Vec3(1.9, 1.9)[int] == Vec3(1, 1, 0)
