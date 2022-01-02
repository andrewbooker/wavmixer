from fader import FadeUpDown


def test_fades_up_from_the_beginning_of_a_block():
    fad = FadeUpDown(rampTime=1.0, startTime=0, upTime=99999, sampleRate=5)

    b = [[1.0]] * 5
    assert [fad.apply(s) for s in b] == [[0.0], [0.2], [0.4], [0.6], [0.8]]


def test_maintains_level_after_fade_up():
    fad = FadeUpDown(rampTime=1.0, startTime=0, upTime=99999, sampleRate=5)

    assert [fad.apply(s) for s in [[1.0]] * 5] == [[0.0], [0.2], [0.4], [0.6], [0.8]]
    assert [fad.apply(s) for s in [[1.0]] * 5] == [[1.0]] * 5


def test_fades_down_from_the_beginning_of_a_block():
    fad = FadeUpDown(rampTime=1.0, startTime=0, upTime=1, sampleRate=5)

    assert [fad.apply(s) for s in [[1.0]] * 5] == [[0.0], [0.2], [0.4], [0.6], [0.8]]
    assert [fad.apply(s) for s in [[1.0]] * 5] == [[1.0]] * 5
    assert [fad.apply(s) for s in [[1.0]] * 5] == [[0.8], [0.6], [0.4], [0.19999999999999996], [0.0]]


def test_fades_within_blocks():
    fad = FadeUpDown(rampTime=1.0, startTime=0.5, upTime=1, sampleRate=4)
    
    assert [fad.apply(s) for s in [[0.4]] * 4][2:] == [[0.0], [0.1]]
    assert [fad.apply(s) for s in [[0.4]] * 4] == [[0.2], [0.30000000000000004], [0.4], [0.4]]
    assert [fad.apply(s) for s in [[0.4]] * 4] == [[0.4], [0.4], [0.30000000000000004], [0.2]]
    assert [fad.apply(s) for s in [[0.4]] * 4][:2] == [[0.1], [0.0]]