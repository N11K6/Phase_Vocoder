# Phase Vocoder:

This little program is a phase vocoder - an algorithm capable of changing the duration of an audio file without altering its pitch, or changing its pitch without altering its duration. 

* **audio_files** directory contains a number of audio files that can be used for testing the program, as well as some output examples for both time stretching and pitch shifting implementations.
* *phasevox.py* contains the phase vocoder as a function that can be imported into any python script. If run as a program, it will require some audio input, and will produce a *.wav* file of the modified audio.
* *phasevox_app.py* is the code for a **streamlit** based web browser application of the phase vocoder. It requires streamlit to be installed as a library in the local machine *(pip install streamlit)* and can be run from the shell command via: *$ streamlit run phasevoc_app.py*.

\* More documentation, and hopefully a more versatile app version to come soon.
