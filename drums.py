from pippi import dsp, noise, oscs

def bln(length, low=3000.0, high=7100.0, wform='sine'):
    return noise.bln(wform, length, low, high)

def eu(length, numpulses):
    pulses = [ 1 for pulse in range(numpulses) ]
    pauses = [ 0 for pause in range(length - numpulses) ]

    position = 0
    while len(pauses) > 0:
        try:
            index = pulses.index(1, position)
            pulses.insert(index + 1, pauses.pop(0))
            position = index + 1
        except ValueError:
            position = 0

    return pulses

def hihat(amp, length):
    if amp == 0:
        return dsp.buffer(length=length)

    def hat(length):
        lowf = dsp.rand(6000, 11000)
        highf = dsp.rand(11000, 17000)

        if dsp.rand() > 0.5:
            length *= 0.05
        
        out = bln(length, lowf, highf)
        out = out.env(dsp.choice(['rsaw', 'phasor', 'hannout']))

        return out

    if dsp.rand() > 0.5:
        out = dsp.join([ hat(length / 2), hat(length / 2) ])
    else:
        out = hat(length)

    return out

def snare(amp, length):
    if amp == 0:
        return dsp.buffer(length=length)

    # Two layers of noise: lowmid and high
    out = dsp.mix([ bln(int(length * 0.2), 700, 3200, 'impulse'), bln(int(length * 0.01), 7000, 9000) ])
    
    out = out.env('phasor')
    out = out.pad(end=length - out.dur)

    return out

def kick(amp, length):
    if amp == 0:
        return dsp.buffer(length=length)

    out = oscs.Osc('sine', freq=dsp.win('rsaw', 60, 160)).play(length).env('phasor')
    return out

def clap(amp, length):
    if amp == 0:
        return dsp.buffer(length=length)

    # Two layers of noise: lowmid and high
    out = dsp.mix([ bln(int(length * 0.2), 600, 1200), bln(int(length * 0.2), 7000, 9000) ])
    out = out.env('phasor').pad(end=length - out.dur)

    return out

def make(drum, pat, lengths):
    events = [ [pat[i], lengths[i]] for i in range(len(pat)) ]

    if len(events) > 0:
        out = dsp.join([ drum(event[0] * 0.3, event[1]) for event in events ])
    else: 
        print(lengths, pat)
        out = dsp.buffer(length=sum(lengths))

    return out

