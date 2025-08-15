# -*- coding: utf-8 -*-
"""
PhaseVox: 
    A function to implement a standard Phase Vocoder for time stretching, or
    pitch shifting an audio file.

@author: NK
"""
#&& Dependencies:
import numpy as np
import librosa as lb
import soundfile as sf
#%%
def PhaseVox(audio_file, Q, mode = 'time'):
    '''
    Function to implement a Phase Vocoder algorithm in order to either: 
    
        1. Perform time stretching (or squeezing) on a sound file, while
    preserving its perceived pitch.
    
        2. Alter its pitch without changing its duration.
    
    args:
        audio_file (string): path to an input audio file
        Q (float): stretch factor (>1 to stretch, <1 to squeeze)
        mode (string): either 'time' or 'pitch' depending on the function
        
    returns:
        y : numpy array (float32) containing the stretched signal
        sample_rate : the sample rate for the output signal
        
    Suggested usage: call PhaseVox as a function:
    
        y, sample_rate = PhaseVox("path/to/audio.wav", Q, "mode")
        
        Then, soundfile.write or another python proecess can be used to write the 
        y array into an audio file using sample_rate as the sample rate.
    '''
    # Load input:
    x, sample_rate = lb.load(audio_file, sr = None)
      
    # Window length:
    N = 2048
    # Create Hann window:
    window = 0.5 * (1 - np.cos(2 * np.pi * np.arange(N) / N))
    
    # Synthesis Hop:
    H_Synth = N // 8
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
        
        # Temporary sample rate for the different signal length:
        sample_rate_p = int(sample_rate * Q)
        # Resample output signal to the original sample rate:
        y = lb.resample(y, orig_sr=sample_rate_p, target_sr=sample_rate)
    
    return y, sample_rate
#%%
if __name__ == "__main__":
    # Load an audio file:
    audio_file = './audio_files/example_phrase.wav'
    # Set vocoder mode:
    mode = 'pitch' # or 'pitch'
    # Set stretch/shift factor:
    Q = 1.5 # >1 for stretch, <1 for squeeze/shift down
    # Get modified signal:
    y, sample_rate = PhaseVox(audio_file, Q, mode=mode)
    # Write into .wav file:
    sf.write('./audio_files/PhaseVox_out_' + mode + '.wav', y, sample_rate)
