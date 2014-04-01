# Copyright (C) 2006-2013  Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of Essentia
#
# Essentia is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation (FSF), either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the Affero GNU General Public License
# version 3 along with this program. If not, see http://www.gnu.org/licenses/

from essentia.standard import *
import essentia
import numpy as np 
import sys
from essentia import INFO
from essentia.progress import Progress
import matplotlib.pyplot as plt
import scipy.signal as signal

namespace = 'rhythm'
dependencies = None

def computeNsdf(audio,options):
    sampleRate  = options['sampleRate']
    frameSize   = options['frameSize']
    hopSize     = options['hopSize']
    zeroPadding = options['zeroPadding']
    windowType  = options['windowType']

    frameRate = float(sampleRate)/float(hopSize)

    INFO('Computing Onset Detection...')

    frames  = FrameGenerator(audio = audio, frameSize = frameSize, hopSize = hopSize)
    window  = Windowing(size = frameSize, zeroPadding = zeroPadding, type = windowType)
    nsdff = Nsdf()
    fftf = Spectrum()
    crestf = Crest()
    instPowf = InstantPower()
    
    total_frames = frames.num_frames()
    n_frames = 0
    start_of_frame = -frameSize*0.5


    progress = Progress(total = total_frames)
    cr = []
    env = []
    for frame in frames:

        windowed_frame = window(frame)
        nsdf = nsdff(frame)
        fftn = fftf(nsdf)
        cr += [crestf(fftn)]
        pow = instPowf(frame)
        
        if len(cr)>2 and pow<0.000001:
            
            cr[-1]=cr[-2]
        

        n_frames += 1
        start_of_frame += hopSize

    
    cr = np.array(cr)
#     w = signal.gaussian(3,1)
#     area = np.sum(w)
#     cr =np.convolve(cr,w , 'same')
#     cr = cr/(100.*area)
    return cr
    
def computeEss(audio, options):

    sampleRate  = options['sampleRate']
    frameSize   = options['frameSize']
    hopSize     = options['hopSize']
    zeroPadding = options['zeroPadding']
    windowType  = options['windowType']

    frameRate = float(sampleRate)/float(hopSize)

    INFO('Computing Ess Detection...')

    frames  = FrameGenerator(audio = audio, frameSize = frameSize, hopSize = hopSize)
    window  = Windowing(size = frameSize, zeroPadding = zeroPadding, type = windowType)
    fft = FFT()
    cartesian2polar = CartesianToPolar()
    onsetdetectionHFC = OnsetDetection(method = "hfc", sampleRate = sampleRate)
    onsetdetectionComplex = OnsetDetection(method = "complex", sampleRate = sampleRate)
    

    total_frames = frames.num_frames()
    n_frames = 0
    start_of_frame = -frameSize*0.5

    hfc = []
    complex = []

    progress = Progress(total = total_frames)
    maxhfc=0 
    
    for frame in frames:

        windowed_frame = window(frame)
        complex_fft = fft(windowed_frame)
        (spectrum,phase) = cartesian2polar(complex_fft)
        hfc.append(onsetdetectionHFC(spectrum,phase))
        maxhfc = max(hfc[-1],maxhfc)
        complex.append(onsetdetectionComplex(spectrum,phase))

        # display of progress report
        progress.update(n_frames)

        n_frames += 1
        start_of_frame += hopSize

    # The onset rate is defined as the number of onsets per seconds
    res = [[x/maxhfc for x in hfc]]
    res +=[complex]
   
    return res





    
    
    