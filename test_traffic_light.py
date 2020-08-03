from trafficlight import TrafficLight


def test_start_state_is_arbitrarily_ns_green():
    l = TrafficLight()
    assert l.ns == '🟢⚫⚫'
    assert l.ew == '⚫⚫🔴'
