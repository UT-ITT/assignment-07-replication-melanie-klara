# Paper Selection

## SoundWave

We considered multiple papers for the paper selection with all of them having something to do with gesture based mouse control.
The first paper is [SoundWave: using the doppler effect to sense gestures](https://doi.org/10.1145/2207676.2208331). It proposes a system where the microphone and the speaker of a computer are used to create an inaudible ultrasonic sound. If an object, such as a hand, moves in front of the computer, the frequency changes due to the doppler effect. This is how gestures are detected. However, this approach is highly dependent on the used hardware, especially the microphone and speaker. These differ a lot when comparing different computers and due to the system being subsceptible to background noise it is very likely that it would not produce reliable output.

## Gaze+Gesture

The second option was the paper [Gaze+Gesture: Expressive, Precise and Targeted
Free-Space Interactions](http://dx.doi.org/10.1145/2818346.2820752). The paper makes use of an eye-tracker to let users select an object on screen via their gaze. Then a hand gesture executes an action. However, for this system a precise eye-tracker is necessary as well as hand tracking sensors which are not available to us.

## Hand Gesture Based Virtual Mouse

This is why we decided to implement the system proposed by the paper [Design and Development of Hand Gesture Based
Virtual Mouse](https://doi.org/10.1109/ICASERT.2019.8934612). It is also about using hand gestures to control the mouse, but it makes use of colored finger tips to detect a gesture, which doesn't require some special kind of hardware. Since the paper works a lot with the openCV library, which we already used a lot, the project is very doable in the given time.

<br>

# Implementation

## Color-Based Finger Tracking

The first step of the implementation was detecting the colored marker in the user's finger, following the approach described in the selected paper. This approach allows the application to run in real time with low computational requirements and only using a standard webcam and a tracker that can be just a piece of colored paper, a sticker or even painting your finger

We use the OpenCV library for image acquisition and processing, since it provides the functions for real-time image processing, object detection and tracking that are required for the implementation. Using these built-in functions reduced development time while ensuring good real-time performance.

Each frame captured by the webcam is mirrored horizontally to create a more natural interaction, where moving the finger to the right also moves the cursor to the right. The frame is then converted from the BGR color space to HSV. We chose the HSV color space because it separates color information from brightness, making a more robust and reliable color segmentation.

After the conversion, a binary mask is generated using a HSV range that corresponds to the color of the marker. Pixels within the selected range appear white in the mask, while all other pixels are black. 

Once the mask has been generated, OpenCV's contour detection is used to identify the largest object, which is assumed to be the colored marker, since the marker is expected to be the most prominent object of the selected colot. Small contours below a predefined area threshold are ignored to reduce false detections and improve stability of the tracking by eliminating isolated pixels created by image noise. 

A bounding box is then computed around the selected contour. This rectangle provides not only a visual indication of the tracked finger but it also allows the position of the marker to be easily determined. The center point of the marker is calculated using the top-left coordinates and the dimensions of the bounding box. The center point, displayed as a red circle, will later be used to control the mouse cursor.

## Calibration

We chose a standard HSV threshold for a green marker in well lit conditions but during testing, it quickly became apparent that using fixed HSV values was unreliable since the lighting conditions and camera quality can change the appearance of the marker resulting in inaccurate and unstable tracking. 

To adress this issue we created a calibration mode.

The calibration mode allows the user to determine the HSV thresholds appropiate for the lighting conditions and the color of the marker bieng used. The calibration window shows 6 sliders that control the minimum and maximun values for hue, saturation and value, as well as a live binary mask of th camera feed. The user adjusts these sliders until only the desired marker appears white and the rest of the image stays black.

Once the calibration is accepted, the selected HSV values are stored and used for marker tracking.

We chose a manual calibration over other methods because giving the user direct control over the HSV thresholds created a more reliable tracking across different cameras and lighting conditions and it was also simpler to implement. This method also allows the adaptation of the application for different color markers without modifying the source code.

## User Interface

To make the application easier to use and to separate calibration from tracking, we implemented a menu system to allow the user to switch between the different modes. This prevents accidental changes to the HSV thresholds and provides a clear workflow for the user. 

When first opening the application the main menu is shown, here the user has multiple options. Keyboard controls were chosen because they are easy to implement and are efficient.
- C: enter calibration mode
- S: start mouse tracking mode
- Q: quit the application

Inside the calibration mode, the user has two options:
- Enter: save the calibrated HSV values
- ESC: cancel calibration and return to menu

In the mouse tracking mode, the user can also use ESC to return to menu.
Pressing Q at any time closes the application.


