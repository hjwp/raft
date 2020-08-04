from typing import Dict, Union, Literal, Callable
MaybeState = Union[Dict, Literal[False]]

Init = {
    'state': 'G1',
    'clock': 0,
    'button': False,
}


G1 = lambda s: (
    False if s['state'] != 'G1'
    else (
        {**s, 'clock': s['clock'] + 1} if s['clock'] < 30
        else
        {**s, 'state': 'Y1', 'clock': 0} if s['clock'] == 30
        else
        False
    )
)   # type: Callable[[Dict], MaybeState]

Y1 = lambda s: (
    s['state'] == 'Y1' and (
        s['clock'] < 5 and {**s, 'clock': s['clock'] + 1}
        or
        s['clock'] == 5 and {**s, 'state': 'G2', 'clock': 0}
    )
)   # type: Callable[[Dict], MaybeState]

G2 = lambda s: (
    s['state'] == 'G2' and (
        s['clock'] < 60 and {**s, 'clock': s['clock'] + 1}
        or
        s['clock'] == 60 and {**s, 'state': 'Y2', 'clock': 0}
    )
)   # type: Callable[[Dict], MaybeState]

Y2 = lambda s: (
    s['state'] == 'Y2' and (
        s['clock'] < 5 and {**s, 'clock': s['clock'] + 1}
        or
        s['clock'] == 5 and {**s, 'state': 'G1', 'clock': 0}
    )
)   # type: Callable[[Dict], MaybeState]

Next = lambda s: G1(s) or Y1(s) or G2(s) or Y2(s) # type: Callable[[Dict], MaybeState]
