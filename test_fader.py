from fader import FadeUpDown


def test_fades_up_from_the_beginning_of_a_block():
    fader = FadeUpDown(rampTime=1.0, startTime=0, upTime=99999, sampleRate=5)

    b = [[1.0]] * 5
    assert [fader.apply(s) for s in b] == [[0.0], [0.2], [0.4], [0.6], [0.8]]


def test_maintains_level_after_fade_up():
    fader = FadeUpDown(rampTime=1.0, startTime=0, upTime=99999, sampleRate=5)

    assert [fader.apply(s) for s in [[1.0]] * 5] == [[0.0], [0.2], [0.4], [0.6], [0.8]]
    assert [fader.apply(s) for s in [[1.0]] * 5] == [[1.0]] * 5


def test_fades_down_from_the_beginning_of_a_block():
    fader = FadeUpDown(rampTime=1.0, startTime=0, upTime=1, sampleRate=5)

    [fader.apply(s) for s in [[1.0]] * 5]
    [fader.apply(s) for s in [[1.0]] * 5]
    assert [fader.apply(s) for s in [[1.0]] * 5] == [[0.8], [0.6], [0.4], [0.19999999999999996], [0.0]]