#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 13:59:11 2021

@author: nk
"""

#%%
import streamlit as st
import numpy as np
import librosa as lb
import soundfile as sf
#%%

st.title('PhaseVox: \n A phase vocoder for time-stretching and pitch-shifting')

input_audio = st.file_uploader('Upload your audio file:', type = ['wav','mp3'])

if input_audio:
    x, sample_rate = lb.load(input_audio, sr = None)
    sf.write('./audio_files/input_audio.wav', x, sample_rate)
    st.audio('./audio_files/input_audio.wav')
    st.write('Input sample rate: ', sample_rate)

#%%
selected_mode = st.selectbox('Choose function:', 
                    options = ('time stretching', 'pitch shifting'))

if selected_mode == 'pitch shifting':
    mode = 'pitch'

    Q_meaning = 'pitch shifting factor'

else:
    mode = 'time'
    
    Q_meaning = 'time stretching factor'

Q = st.slider(Q_meaning+':', min_value = 0.05, max_value = 2.0, value = 1.0, step = 0.05)

#%%


N = st.selectbox('Window length (samples):',
                 options = (512, 1024, 2048, 4096),
                 index = 2)
H_Choice = st.selectbox('Hop length (relative to window):', 
                        options = ('1/2', '1/4', '1/8', '1/12'),
                        index = 2)
H_Denom = int(H_Choice[-1])

#%%
applied_status = False

if st.button('Apply'):
    # Create Hann window:
    window = 0.5 * (1 - np.cos(2 * np.pi * np.arange(N) / N))
    
    # Synthesis Hop:
    H_Synth = N // H_Denom
    # Analysis Hop:
    H_Analysis = int(np.floor(H_Synth / Q))
    
    # Original length in samples:
    len_x =len(x)
    
    # Number of analysis frames:
    N_frames = int(np.floor((len_x - N) / H_Analysis))
    
    # Initialize output array:
    y = np.zeros((N_frames-1) * H_Synth + N, dtype = complex)
    
    # 2pi for convenience:
    two_pi = 2 * np.pi
    
    # Phase vector
    Pha_vec = np.arange(N) * two_pi * H_Analysis / N
    
    # Initialize loop parameters:
    first_frame = True
    ind_x = 0
    ind_y = 0
    
    Pha_prev = None
    PhaSy_prev = None
    
    #%% Loop:
    for index in range(N_frames):
        
        # Synthesize the first frame:
        if first_frame:
            # Implement window over input:
            x_frame = x[ind_x:N] * window
            # Frequency domain:
            X = np.fft.fft(x_frame)
            # Get magnitude:
            Mag = np.abs(X)
            # Get phase:
            Pha = np.angle(X)
            # Synthesis phase:
            PhaSy = Pha
            # 1st frame is done:
            first_frame = False
            # Placeholder for polar-to-cartesian phase conversion:
            Z = 1
        
        # Synthesize all subsequent frames:
        else:
            # Window over the next frame:
            x_frame = x[ind_x:ind_x + N] * window
            # FFT:
            X = np.fft.fft(x_frame)
            # Magnitude:
            Mag = np.abs(X)
            # Phase:
            Pha = np.angle(X)
            # Get phase difference from previous frame:
            Pha_diff = Pha - Pha_prev - Pha_vec
            # Convert within circle range (-pi,pi):
            Pha_circ = Pha_diff - two_pi * Pha_diff // two_pi
            # Rescale the phase using stretch factor:
            Pha_stretch = (Pha_vec + Pha_circ) * Q
            # Synthesize the new phase for the frame:
            PhaSy = PhaSy_prev + Pha_stretch
            
            # Calculate phase difference:
            theta = PhaSy - Pha
            # Polar to cartesian:
            Z = np.exp(1j * theta)
        
        # Resynthesize in frequency domain:
        Y = Z * X
        # Convert back to time domain:
        y_frame = np.fft.ifft(np.real(Y)) * window
        # Overlapp and add the new frames:
        y[ind_y:ind_y+N] = y[ind_y:ind_y+N] + y_frame
        
        # Update phase info and indices for next loop iteration:
        Pha_prev = Pha
        PhaSy_prev = PhaSy
        ind_x = ind_x + H_Analysis
        ind_y = ind_y + H_Synth
        
        #index ++1
        # Loop ends here.

#%%
    # Keep real part:
    y = np.real(y)
    # Normalize to the same level as the original file:
    y = np.max(np.abs(x)) * y / np.max(np.abs(y))
    # Convert to float32
    y = y.astype('float32')
    
    # In case of pitch shifting mode:
    if mode == 'pitch':
        sample_rate = int(sample_rate * Q)
    
    # Signify to user that phase vocoder was applied:
    st.write('Applied phase vocoder with a ', 
             Q_meaning, ' of ', Q)
    
    applied_status = True
    
    sf.write('./audio_files/output_audio.wav', y, sample_rate)
#%%
if applied_status:
    st.audio('./audio_files/output_audio.wav')
