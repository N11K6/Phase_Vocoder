# Phase Vocoder:

This little program is a phase vocoder - an algorithm capable of changing the duration of an audio file without altering its pitch, or changing its pitch without altering its duration. 

### Usage: 

The program is used to read an input audio file, and, given its function mode and Q factor, apply changes and output the modified audio.
The function mode can be either "time" or "pitch". Q factor can take positive float values, 1 being equivalent to no modification of the file other than analysis into frames and resynthesis.

* "time" : Changes the duration of the file without altering pitch. Q < 1 corresponds to squeezing, Q > 1 corresponds to stretching.
* "pitch" : Changes the pitch of the audio without altering its duration and sample rate. Q < 1 lowers the pitch, Q > 1 raises it.

### Contents:

* *audio_files* directory contains a number of audio files that can be used for testing the program, as well as some output examples for both time stretching and pitch shifting implementations.
* **phasevox.py** contains the phase vocoder as a function that can be imported into any python script. If run as a program, it will require some audio input, and will produce a *.wav* file of the modified audio.
* **phasevox_app.py** is the code for a **streamlit** based web browser application of the phase vocoder. It requires streamlit to be installed as a library in the local machine *(pip install streamlit)* and can be run from the shell command via: *$ streamlit run phasevoc_app.py*.

\* Currently, the app version requires streamlit to be installed locally in order to function. I am currently working on making this a more portable web browser app. 
