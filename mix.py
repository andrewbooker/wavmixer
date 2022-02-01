#!/usr/bin/env python

import soundfile as sf
import sys
import os
from audiofile import AudioFile, FileReader
import json

class SfReader(FileReader):
    def __init__(self, fqfn):
        self.file = sf.SoundFile(fqfn, "r")

    def read(self, samples):
        return self.file.read(samples)

    def close(self):
        self.file.close()

def limit(s):
    threshold = 0.8
    assumedMax = max(1.5, s)
    if abs(s) < threshold:
        return s

    r = threshold + ((abs(s) - threshold) * (1.0 - threshold) / (assumedMax - threshold))
    return -r if s < 0 else r

def merge(b1, b2):
    return [[limit(b1[i][0] + b2[i][0]), limit(b1[i][1] + b2[i][1])] for i in range(len(b1))]


workingDir = sys.argv[1]
cuesFn = sys.argv[2] if len(sys.argv) > 2 else os.path.join(workingDir, "cues.json")
outBase = os.path.basename(cuesFn).split(".")[0]
ac = open(cuesFn)
cues = json.load(ac)
ac.close()

outDir = workingDir

print("writing %s_(L|R).wav" % outBase, "to", outDir)

audioFiles = []
for c in cues:
    fqfn = os.path.join(workingDir, c["file"])
    audioFiles.append(AudioFile(fqfn, SfReader(fqfn), c["fileStart"], c["mixStart"], c["duration"], 0.75))
    

SAMPLE_RATE = 44100
done = False
t = 0
outFileL = sf.SoundFile(os.path.join(outDir, "%s_L.wav" % outBase), "w", samplerate=SAMPLE_RATE, channels=1)
outFileR = sf.SoundFile(os.path.join(outDir, "%s_R.wav" % outBase), "w", samplerate=SAMPLE_RATE, channels=1)
started = False
while not done:
    doneAll = True
    b = [[0.0, 0.0]] * SAMPLE_RATE
    for f in audioFiles:
        if not f.done:
            doneAll = False
            if f.occursInBlockStarting(t):
                started = True
                b = merge(f.nextBlock(t), b)

    outFileL.write([s[0] for s in b])
    outFileR.write([s[1] for s in b])
    t += 1
    done = started and doneAll

outFileL.close()
outFileR.close()

for a in audioFiles:
    del a
