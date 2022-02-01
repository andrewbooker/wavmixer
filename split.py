#!/usr/bin/python

import soundfile as sf
import sys
import os

SAMPLE_RATE=44100

fn = sys.argv[1]
dataSf, ignore = sf.read(fn)
totalLength = len(dataSf)

outDir = "."
outFileL = sf.SoundFile(os.path.join(outDir, "split_L.wav"), "w", samplerate=SAMPLE_RATE, channels=1)
outFileR = sf.SoundFile(os.path.join(outDir, "split_R.wav"), "w", samplerate=SAMPLE_RATE, channels=1)

def sampleAt(i):
    return dataSf[i] if i < len(dataSf) else [0.0, 0.0]

done = False
blockSize = 44100
blockIdx = 0
while not done:
    pos = blockIdx * blockSize
    blockL = [sampleAt(i + pos)[0] for i in range(blockSize)]
    blockR = [sampleAt(i + pos)[1] for i in range(blockSize)]
    outFileL.write(blockL)
    outFileR.write(blockR)
    done = pos > totalLength
    blockIdx += 1

outFileL.close()
outFileR.close()
print("done")
