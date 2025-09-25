from app.utils.timecode import to_seconds, to_timecode


def test_to_seconds_and_back():
    value = to_seconds('00:01:30.500')
    assert abs(value - 90.5) < 0.001
    timecode = to_timecode(value)
    assert timecode.startswith('00:01:30')


def test_invalid_timecode():
    import pytest

    with pytest.raises(ValueError):
        to_seconds('invalid')
