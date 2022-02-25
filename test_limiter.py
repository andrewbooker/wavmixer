from limiter import Limiter

def test_low_value_is_unchanged_at_unity_gain():
    assert Limiter(1.0).apply(0.5) == 0.5

def test_low_value_is_reduced_by_gain_below_unity():
    assert Limiter(0.8).apply(0.5) == 0.4

def test_low_value_is_increased_by_gain_above_unity():
    assert Limiter(1.2).apply(0.5) == 0.6

def test_value_above_threshold_is_attenuated():
    assert round(Limiter(gain=1.0, threshold=0.8, assumedMax=1.2).apply(0.9), 2) == 0.85
    assert round(Limiter(gain=1.0, threshold=0.8, assumedMax=1.6).apply(0.9), 6) == 0.825
    assert round(Limiter(gain=1.0, threshold=0.8, assumedMax=1.8).apply(0.9), 6) == 0.82
    assert Limiter(gain=1.0, threshold=0.8, assumedMax=1.2).apply(1.0) == 0.9
    assert Limiter(gain=1.0, threshold=0.8, assumedMax=1.6).apply(1.0) == 0.85

def test_value_equal_to_assumed_max_is_attenuated_to_one():
    assert Limiter(gain=1.0, threshold=0.8, assumedMax=1.2).apply(1.2) == 1.0
    assert Limiter(gain=1.0, threshold=0.5, assumedMax=1.5).apply(1.5) == 1.0

def test_value_above_assumed_max_is_clipped_to_one():
    assert Limiter(gain=1.0, threshold=0.8, assumedMax=1.2).apply(1.4) == 1.0
    assert Limiter(gain=1.0, threshold=0.8, assumedMax=1.0).apply(2.0) == 1.0
