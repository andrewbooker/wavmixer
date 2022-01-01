from audiofile import *

class StereoRampFileReader(FileReader):
    def __init__(self):
        self.pos = 0

    def sampleRate(self):
        return 4

    def read(self, samples):
        s = []
        self.pos += samples
        for n in range(samples):
            s.append([n / 4.0, n / 4.0])
        return s
        


def test_includes_first_sample_at_time_zero():
    audioFile = AudioFile("", StereoRampFileReader(), 0, 0, 1)
    assert audioFile.occursInBlockStarting(0) == True

def test_reads_one_second_block():
    audioFile = AudioFile("", StereoRampFileReader(), 0, 0, 1)
    b = audioFile.nextBlock(0)
    assert b == [[0.0, 0.0], [0.25, 0.25], [0.5, 0.5], [0.75, 0.75]]
