from pippi import dsp
from pippi import tune
import glob

notes = [ dsp.read(note).data for note in glob.glob('amber/note*') ]

speeds = [ 1.0, 1.5, 2.0 ]
scale = tune.fromdegrees([1, 4, 5, 6, 8, 9], octave=3, root='e')
envs = ['line', 'tri', 'hann', 'phasor', 'impulse']
wforms = ['tri', 'saw', 'impulse', 'square']

layer = [ dsp.randchoose(notes) for i in range(40) ]
layer = [ dsp.pan(note, dsp.rand()) for note in layer ]
layer = [ dsp.amp(note, dsp.rand(0.1, 0.7)) for note in layer ]
layer = [ dsp.transpose(note, dsp.randchoose(speeds)) for note in layer ]
layer = [ dsp.pad(note, 0, dsp.mstf(dsp.rand(500, 2000))) for note in layer ]
layer = ''.join(layer)

dsp.write(layer, 'layer-amber')

lcurve = dsp.breakpoint([ dsp.rand() for l in range(100) ], 2000)
lcurve = [ dsp.mstf(length * 60 + 160) for length in lcurve ]

out = ''

# Break curve into variable size groups
segments = []
count = 0
minseg = 1
maxseg = 20
while count < len(lcurve):
    segsize = dsp.randint(minseg, maxseg)
    seg = lcurve[count : count + segsize]
    segments += [ seg ]

    count += segsize

print len(segments)

# Transpose source guitar melody
speeds = [ 1.0, 1.5, 1.25, 1.333 ]
notes = [ dsp.transpose(note, dsp.randchoose(speeds)) for note in notes * 2 ] 

for i, seg in enumerate(segments):
    segsounds = []
    for length in seg:
        sounds = [ dsp.cut(layer, dsp.randint(0, dsp.flen(layer) - length), length) for s in range(6) ]
        sounds = dsp.mix(sounds)
        segsounds += [ sounds ]

    tlen = sum(seg)

    note = notes[i % len(notes)]

    if dsp.randint(0, 5) != 0:
        note = dsp.fill(note, tlen)

    sounds = dsp.mix([ ''.join(segsounds), note ])

    out += sounds

dsp.write(out, 'amber')
