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
    l = TrafficLight(1)
    assert l.time_til_next == 30
    l.next()
    assert l.time_til_next == 5
    l.next()
    assert l.time_til_next == 60
    l.next()
    assert l.time_til_next == 5
    l.next()
    assert l.time_til_next == 30


def test_push_button():
    l = TrafficLight()
    assert l.time_til_next == 30
    l.push_button()
    assert l.time_til_next == 30

    l.next()
    l.next()
    assert l.time_til_next == 60
    l.push_button()
    assert l.time_til_next == 30


def test_push_button_only_shortens_to_30_secs():
    l = TrafficLight()
    l.next()
    l.next()
    assert l.time_til_next == 60

    l.time_til_next = 31
    l.push_button()
    assert l.time_til_next == 1

    l.time_til_next = 29
    l.push_button()
    assert l.time_til_next == 0


def test_handle_clock_tick():
    l = TrafficLight()
    l.time_til_next = 0
    l.handle_clock_tick()
    assert l.ns == '⚫🟡⚫'
    assert l.ew == '⚫⚫🔴'
