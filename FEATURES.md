Read the project's CRUSH.md and README.md files for general project guidelines while implementing this feature.

Using this project as a guide:
- /bluestone/src/github/rtd/listen

Instead of integrating the voice recording and transcription using python modules directly in the mychatui project. Can we use the venv (Python 3.11) environment in /bluestone/src/github/rtd/listen and run it's listen command. That "listen" command should display a UI window to record the voice and then output the transcribed text to standard output. This should allow the mychatui UI to run under Python3.14 and faster-whisper to run under Python3.11. Let's rewrite the integration to use this strategy please.

Integrate a button with a microphone icon in the chat text entry box, to accept voice input for a "chat message".

When microphone icon is pressed, the UI will indicate it is listening and record audio from the first microphone on the PC using pyaudio. If
the best means of providing the UI feedback of listening is to pop up a new UI window or to activate a UI element
at the bottom of the UI, I will leave that choice to you based on ease of implementing of the feature.

It would be nice if a sine wave was animated when input is received from the microphone (if possible). If this isn't possible
don't worry about it.

The voice recording will be transcribed to text using faster-whisper python module. The transcribed text will
be displayed in the chat message text entry box for the user to confirm to send to the LLM using the text boxes
normal submission method.

Write an integration test, for testing the voice recording / transcription components of the solution.
