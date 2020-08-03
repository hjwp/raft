import time
from trafficlight import TrafficLight


def test_start_state_is_arbitrarily_ns_green():
    l = TrafficLight()
    assert l.ns == '🟢⚫⚫'
    assert l.ew == '⚫⚫🔴'


def test_full_cyclye():
    l = TrafficLight()
    assert l.ns == '🟢⚫⚫'
    assert l.ew == '⚫⚫🔴'
    l.next()
    assert l.ns == '⚫🟡⚫'
    assert l.ew == '⚫⚫🔴'
    l.next()
    assert l.ns == '⚫⚫🔴'
    assert l.ew == '🟢⚫⚫'
    l.next()
    assert l.ns == '⚫⚫🔴'
    assert l.ew == '⚫🟡⚫'
    l.next()
    assert l.ns == '🟢⚫⚫'
    assert l.ew == '⚫⚫🔴'


def test_time_til_next():
    l = TrafficLight()
    assert l.time_til_next == 30
    l.next()
    assert l.time_til_next == 5
    l.next()
    assert l.time_til_next == 60
    l.next()
    assert l.time_til_next == 5
    l.next()
    assert l.time_til_next == 30


# def test_is_time_yet():
#     start = time.time()
#     l = TrafficLight()
#     assert l.is_time_yet(time.time()) is False
#     assert l.is_time_yet(start + 28) is False
#     assert l.is_time_yet(start + 31) is True


def test_push_button():
    l = TrafficLight()
    l.next()
    l.next()
    assert l.ns == '⚫⚫🔴'
    assert l.ew == '🟢⚫⚫'
    assert l.time_til_next == 60
    l.push_button()
    assert l.time_til_next == 30
