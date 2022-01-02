from audiofile import *


class BaseReader(FileReader):
    def __init__(self, s):
        self.s = s
        self.pos = 0

    def sampleRate(self):
        return 4

    def read(self, samples):
        s = self.s[self.pos:self.pos + samples]
        self.pos += samples
        return s


class StereoRampFileReader(BaseReader):
    def __init__(self, length=1):
        denominator = 4.0 * length
        super(StereoRampFileReader, self).__init__([[n / denominator, n / denominator] for n in range(int(denominator))])


class StereoFlatReader(BaseReader):
    def __init__(self, value, length=1):
        super(StereoFlatReader, self).__init__([[value, value]] * 4 * length)


def test_includes_first_sample_at_time_zero():
    audioFile = AudioFile("", StereoRampFileReader(), 0, 0, 1)
    assert audioFile.occursInBlockStarting(0) is True


def test_reads_a_one_second_block():
    audioFile = AudioFile("", StereoRampFileReader(), 0, 0, 1)
    b = audioFile.nextBlock(0)
    assert b == [[0.0, 0.0], [0.25, 0.25], [0.5, 0.5], [0.75, 0.75]]
    assert audioFile.done is True


def test_subsequent_reads_are_empty_once_all_required_samples_have_been_read():
    audioFile = AudioFile("", StereoRampFileReader(), 0, 0, 1)
    audioFile.nextBlock(0)
    b = audioFile.nextBlock(1)
    assert b == [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]
    assert audioFile.done is True


def test_reads_nothing_before_the_mix_start():
    audioFile = AudioFile("", StereoRampFileReader(), 0, 2, 1)
    b = audioFile.nextBlock(0)
    assert b == [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]
    assert audioFile.done is False


def test_reads_fragment_of_file_if_it_starts_half_way_through_a_block():
    audioFile = AudioFile("", StereoRampFileReader(), 0, 0.5, 1)
    b = audioFile.nextBlock(0)
    assert b == [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.25, 0.25]]
    assert audioFile.done is False


def test_reads_fragment_of_file_if_it_finishes_half_way_through_a_block():
    audioFile = AudioFile("", StereoRampFileReader(), 0, 0.5, 1)
    audioFile.nextBlock(0)
    b = audioFile.nextBlock(1)
    assert b == [[0.5, 0.5], [0.75, 0.75], [0.0, 0.0], [0.0, 0.0]]
    assert audioFile.done is True


def test_reads_sequence_of_sections_from_a_long_file():
    audioFile1 = AudioFile("", StereoRampFileReader(2), 0.25, 0.5, 1.5)
    assert audioFile1.nextBlock(0) == [[0.0, 0.0], [0.0, 0.0], [0.125, 0.125], [0.25, 0.25]]
    assert audioFile1.nextBlock(1) == [[0.375, 0.375], [0.5, 0.5], [0.625, 0.625], [0.75, 0.75]]

    audioFile2 = AudioFile("", StereoRampFileReader(4), 0.75, 0.5, 2.0)
    assert audioFile2.nextBlock(0) == [[0.0, 0.0], [0.0, 0.0], [0.1875, 0.1875], [0.25, 0.25]]
    assert audioFile2.nextBlock(1) == [[0.3125, 0.3125], [0.375, 0.375], [0.4375, 0.4375], [0.5, 0.5]]
    assert audioFile2.nextBlock(2) == [[0.5625, 0.5625], [0.625, 0.625], [0.0, 0.0], [0.0, 0.0]]

    audioFile3 = AudioFile("", StereoRampFileReader(4), 0.75, 0.5, 2.25)
    assert audioFile3.nextBlock(0) == [[0.0, 0.0], [0.0, 0.0], [0.1875, 0.1875], [0.25, 0.25]]
    assert audioFile3.nextBlock(1) == [[0.3125, 0.3125], [0.375, 0.375], [0.4375, 0.4375], [0.5, 0.5]]
    assert audioFile3.nextBlock(2) == [[0.5625, 0.5625], [0.625, 0.625], [0.6875, 0.6875], [0.0, 0.0]]


def test_can_fade_up_to_the_specified_file_at_the_beginning_of_the_mix():
    audioFile = AudioFile("", StereoRampFileReader(2), 1, 0, 999, 0.5)
    assert audioFile.nextBlock(0) == [[0.0, 0.0], [0.1875, 0.1875], [0.5, 0.5], [0.625, 0.625]]


def test_can_fade_up_samples_prior_to_the_specified_file_start_time_after_the_beginning_of_the_mix():
    audioFile1 = AudioFile("", StereoRampFileReader(2), 1, 1, 999, 0.5)
    assert audioFile1.nextBlock(0) == [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.1875, 0.1875]]

    audioFile2 = AudioFile("", StereoFlatReader(0.4, 9), 1, 1, 999, 0.5)
    assert audioFile2.nextBlock(0) == [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.2, 0.2]]
    assert audioFile2.nextBlock(1) == [[0.4, 0.4], [0.4, 0.4], [0.4, 0.4], [0.4, 0.4]]


def test_can_fade_out_by_the_specified_end_time():
    audioFile = AudioFile("", StereoFlatReader(0.4, 9), 1, 1, 2, 0.5)
    assert audioFile.nextBlock(0) == [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.2, 0.2]]
    assert audioFile.nextBlock(1) == [[0.4, 0.4], [0.4, 0.4], [0.4, 0.4], [0.4, 0.4]]
    assert audioFile.nextBlock(2) == [[0.4, 0.4], [0.4, 0.4], [0.2, 0.2], [0.0, 0.0]]