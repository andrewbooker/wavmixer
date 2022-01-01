from audiofile import *



def test_includes_first_sample_at_time_zero():
    audioFile = AudioFile("", FileReader(), 0, 0, 1)
    assert audioFile.occursInBlockStarting(0) == True
