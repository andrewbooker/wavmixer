from audiofile import *


class StereoRampFileReader(FileReader):
    def __init__(self):
        self.pos = 0
        self.s = [[n / 4.0, n / 4.0] for n in range(4)]

    def sampleRate(self):
        return 4

    def read(self, samples):
        s = self.s[self.pos:self.pos + samples]
        self.pos += samples
        return s


class StereoLongRampFileReader(FileReader):
    def __init__(self, length):
        self.pos = 0
        denominator = 4.0 * length
        self.s = [[n / denominator, n / denominator] for n in range(int(denominator))]

    def sampleRate(self):
        return 4

    def read(self, samples):
        s = self.s[self.pos:self.pos + samples]
        self.pos += samples
        return s
        

def test_includes_first_sample_at_time_zero():
    audioFile = AudioFile("", StereoRampFileReader(), 0, 0, 1)
    assert audioFile.occursInBlockStarting(0) == True


def test_reads_a_one_second_block():
    audioFile = AudioFile("", StereoRampFileReader(), 0, 0, 1)
    b = audioFile.nextBlock(0)
    assert b == [[0.0, 0.0], [0.25, 0.25], [0.5, 0.5], [0.75, 0.75]]
    assert audioFile.done == True


def test_subsequent_reads_are_empty_once_all_required_samples_have_been_read():
    audioFile = AudioFile("", StereoRampFileReader(), 0, 0, 1)
    audioFile.nextBlock(0)
    b = audioFile.nextBlock(1)
    assert b == [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]
    assert audioFile.done == True


def test_reads_nothing_before_the_mix_start():
    audioFile = AudioFile("", StereoRampFileReader(), 0, 2, 1)
    b = audioFile.nextBlock(0)
    assert b == [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]
    assert audioFile.done == False


def test_reads_fragment_of_file_if_it_starts_half_way_through_a_block():
    audioFile = AudioFile("", StereoRampFileReader(), 0, 0.5, 1)
    b = audioFile.nextBlock(0)
    assert b == [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.25, 0.25]]
    assert audioFile.done == False


def test_reads_fragment_of_file_if_it_finishes_half_way_through_a_block():
    audioFile = AudioFile("", StereoRampFileReader(), 0, 0.5, 1)
    audioFile.nextBlock(0)
    b = audioFile.nextBlock(1)
    assert b == [[0.5, 0.5], [0.75, 0.75], [0.0, 0.0], [0.0, 0.0]]
    assert audioFile.done == True


def test_reads_sequence_of_sections_from_a_long_file():
    #audioFile1 = AudioFile("", StereoLongRampFileReader(2), 0.25, 0.5, 1.5)
    #assert audioFile1.nextBlock(0) == [[0.0, 0.0], [0.0, 0.0], [0.125, 0.125], [0.25, 0.25]]
    #assert audioFile1.nextBlock(1) == [[0.375, 0.375], [0.5, 0.5], [0.625, 0.625], [0.75, 0.75]]

    #audioFile2 = AudioFile("", StereoLongRampFileReader(4), 0.75, 0.5, 2.0)
    #assert audioFile2.nextBlock(0) == [[0.0, 0.0], [0.0, 0.0], [0.1875, 0.1875], [0.25, 0.25]]
    #assert audioFile2.nextBlock(1) == [[0.3125, 0.3125], [0.375, 0.375], [0.4375, 0.4375], [0.5, 0.5]]
    #assert audioFile2.nextBlock(2) == [[0.5625, 0.5625], [0.625, 0.625], [0.0, 0.0], [0.0, 0.0]]

    audioFile3 = AudioFile("", StereoLongRampFileReader(4), 0.75, 0.5, 2.25)
    assert audioFile3.nextBlock(0) == [[0.0, 0.0], [0.0, 0.0], [0.1875, 0.1875], [0.25, 0.25]]
    assert audioFile3.nextBlock(1) == [[0.3125, 0.3125], [0.375, 0.375], [0.4375, 0.4375], [0.5, 0.5]]
    assert audioFile3.nextBlock(2) == [[0.5625, 0.5625], [0.625, 0.625], [0.6875, 0.6875], [0.0, 0.0]]