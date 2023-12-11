from mixer import Mixer


class Sink:
    def __init__(self):
        self.vals = []

    def write(self, v):
        self.vals.extend(v)


class ConstCoeffLimiter:
    def __init__(self, coeff):
        self.coeff = coeff

    def apply(self, v):
        return v * self.coeff


class NoOpLimiter(ConstCoeffLimiter):
    def __init__(self):
        ConstCoeffLimiter.__init__(self, 1.0)


class ConstAudioFile:
    def __init__(self, v, active_start, active_end, sample_rate):
        self.val = v
        self.sample_rate = sample_rate
        self.active_start = active_start
        self.active_end = active_end
        self.done = False

    def occursInBlockStarting(self, t):
        if t >= (self.active_end - 1):
            self.done = True
        return self.active_start <= t < self.active_end

    def nextBlock(self, t):
        return [[self.val, self.val]] * self.sample_rate


def test_sums_constant_values():
    sinkL = Sink()
    mixer = Mixer(sinkL, Sink(), NoOpLimiter(), 1)

    file1 = ConstAudioFile(0.2, 2, 4, 1)
    file2 = ConstAudioFile(0.3, 1, 3, 1)

    mixer.mix([file1, file2])

    assert sinkL.vals == [0.0, 0.3, 0.5, 0.2, 0.0]


def test_applies_limiter_to_sum_of_two_wave_values():
    sinkL = Sink()
    mixer = Mixer(sinkL, Sink(), ConstCoeffLimiter(0.5), 1)

    file1 = ConstAudioFile(0.1, 2, 4, 1)
    file2 = ConstAudioFile(0.1, 1, 3, 1)

    mixer.mix([file1, file2])

    assert sinkL.vals == [0.0, 0.05, 0.1, 0.05, 0.0]
