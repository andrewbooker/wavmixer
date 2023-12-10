#!/usr/bin/python

import soundfile as sf
import sys
import os

SAMPLE_RATE=44100

fn1 = sys.argv[1]
fn2 = sys.argv[2]
outFn = sys.argv[3]
f2StartAt = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0

print(fn1)
print(fn2)

dataSf1, ignore1 = sf.read(fn1)
dataSf2, ignore2 = sf.read(fn2)

startOffset = int(f2StartAt * 44100)

totalLength = max(len(dataSf1), len(dataSf2)) + startOffset
print(totalLength)

def sampleAt(i):
    l = dataSf1[i] if i < len(dataSf1) else 0.0
    rIdx = i - startOffset
    r = dataSf2[rIdx] if i >= startOffset and rIdx < len(dataSf2) else 0.0
    return [l, r]

outDir = "."
outFile = sf.SoundFile(os.path.join(outDir, outFn), "w", samplerate=SAMPLE_RATE, channels=2)

done = False
blockSize = 44100
blockIdx = 0
while not done:
    pos = blockIdx * blockSize
    block = [sampleAt(i + pos) for i in range(blockSize)]
    outFile.write(block)
    done = pos > totalLength
    blockIdx += 1


outFile.close()
print("done")
