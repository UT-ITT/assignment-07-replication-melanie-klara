# Paper Selection:

## SoundWave

We considered multiple papers for the paper selection with all of them having something to do with gesture based mouse control.
The first paper is [SoundWave: using the doppler effect to sense gestures](https://doi.org/10.1145/2207676.2208331). It proposes a system where the microphone and the speaker of a computer are used to create an inaudible ultrasonic sound. If an object, such as a hand, moves in front of the computer, the frequency changes due to the doppler effect. This is how gestures are detected. However, this approach is highly dependent on the used hardware, especially the microphone and speaker. These differ a lot when comparing different computers and due to the system being subsceptible to background noise it is very likely that it would not produce reliable output.

## Gaze+Gesture

The second option was the paper [Gaze+Gesture: Expressive, Precise and Targeted
Free-Space Interactions](http://dx.doi.org/10.1145/2818346.2820752). The paper makes use of an eye-tracker to let users select an object on screen via their gaze. Then a hand gesture executes an action. However, for this system a precise eye-tracker is necessary as well as hand tracking sensors which are not available to us.

## Hand Gesture Based Virtual Mouse

This is why we decided to implement the system proposed by the paper [Design and Development of Hand Gesture Based
Virtual Mouse](https://doi.org/10.1109/ICASERT.2019.8934612). It is also about using hand gestures to control the mouse, but it makes use of colored finger tips to detect a gesture, which doesn't require some special kind of hardware. Since the paper works a lot with the openCV library, which we already used a lot, the project is very doable in the given time.
