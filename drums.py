from pippi import dsp

def bln(length, low=3000.0, high=7100.0, wform='sine2pi'):
    """ Time-domain band-limited noise generator
    """
    outlen = 0
    cycles = ''
    while outlen < length:
        cycle = dsp.cycle(dsp.rand(low, high), wform)
        outlen += len(cycle)
        cycles += cycle

    return cycles

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
        return dsp.pad('', 0, length)

    def hat(length):
        lowf = dsp.rand(6000, 11000)
        highf = dsp.rand(11000, 17000)
        
        if dsp.randint(0, 6) == 0:
            out = bln(length, lowf, highf)
            out = dsp.env(out, 'line')
        else:
            out = bln(int(length * 0.05), lowf, highf)
            out = dsp.env(out, 'phasor')
            out = dsp.pad(out, 0, length - dsp.flen(out))

        return out

    if dsp.randint() == 0:
        out = ''.join([ hat(length / 2), hat(length / 2) ])
    else:
        out = hat(length)

    return out

def snare(amp, length):
    if amp == 0:
        return dsp.pad('', 0, length)

    # Two layers of noise: lowmid and high
    out = dsp.mix([ bln(int(length * 0.2), 700, 3200, 'impulse'), bln(int(length * 0.01), 7000, 9000) ])
    
    out = dsp.env(out, 'phasor')
    out = dsp.pad(out, 0, length - dsp.flen(out))

    return out

def kick(amp, length):
    if amp == 0:
        return dsp.pad('', 0, length)

    fhigh = 160.0
    flow = 60.0
    fdelta = fhigh - flow

    target = length
    pos = 0
    fpos = fhigh

    out = ''
    while pos < target:
        # Add single cycle
        # Decrease pitch by amount relative to cycle len
        cycle = dsp.cycle(fpos)
        #cycle = ''.join([ str(v) for v in dsp.curve(0, dsp.htf(fpos), math.pi * 2) ])
        pos += dsp.flen(cycle)
        #fpos = fpos - (fhigh * (length / dsp.htf(fpos)))
        fpos = fpos - 30.0
        out += cycle

    return dsp.env(out, 'phasor')



def clap(amp, length):
    if amp == 0:
        return dsp.pad('', 0, length)

    # Two layers of noise: lowmid and high
    out = dsp.mix([ bln(int(length * 0.2), 600, 1200), bln(int(length * 0.2), 7000, 9000) ])
    
    out = dsp.env(out, 'phasor')
    out = dsp.pad(out, 0, length - dsp.flen(out))

    return out

def make(drum, pat, lengths):
    events = [ [pat[i], lengths[i]] for i in range(len(pat)) ]

    if len(events) > 0:
        out = ''.join([ drum(event[0] * 0.3, event[1]) for event in events ])
    else: 
        print lengths, pat
        out = ''

    return out

