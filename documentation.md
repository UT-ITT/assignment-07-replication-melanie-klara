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

The first step of the implementation was detecting the colored marker in the user's finger, following the approach described in the selected paper. This approach allows the application to run in real time with low computational requirements and only using a standard webcam and a tracker that can be just a piece of colored paper, a sticker or even painting your finger.

We use the OpenCV library for image acquisition and processing, since it provides the functions for real-time image processing, object detection and tracking that are required for the implementation. Using these built-in functions reduced development time while ensuring good real-time performance.

Each frame captured by the webcam is mirrored horizontally to create a more natural interaction, where moving the finger to the right also moves the cursor to the right. The frame is then converted from the BGR color space to HSV. We chose the HSV color space because it separates color information from brightness, making a more robust and reliable color segmentation.

After the conversion, a binary mask is generated using an HSV range that corresponds to the color of the marker. Pixels within the selected range appear white in the mask, while all other pixels are black.

Once the mask has been generated, OpenCV's contour detection is used to identify the largest object, which is assumed to be the colored marker, since the marker is expected to be the most prominent object of the selected color. Small contours below a predefined area threshold are ignored to reduce false detections and improve stability of the tracking by eliminating isolated pixels created by image noise.

Since the paper uses different gestures based on one, two or three markers, we extended the code to detect muliple markers simultaneously. Instead of selecting only the largest contour, we use all detected contours that exceed minimum area threshold and store them in a list of markers. The markers are sorted from left to right to ensure a consistent ordering, this simplifies gesture recognition since each gestures can be identified basedon the number and relative positions of the detected markers.

A bounding box is then computed around the selected contours. This rectangle provides not only a visual indication of the tracked fingers, but it also allows the position of the markers to be easily determined. The center points of the markers are calculated using the top-left coordinates and the dimensions of the bounding boxes. Then, a line is drawn between those center points. The middle of this line is calculated using linear interpolation. This middle point is later used to control the mouse.

## Calibration

We chose a standard HSV threshold for a green marker in well lit conditions but during testing, it quickly became apparent that using fixed HSV values was unreliable since the lighting conditions and camera quality can change the appearance of the marker resulting in inaccurate and unstable tracking.

To address this issue we created a calibration mode.

The calibration mode allows the user to determine the HSV thresholds appropriate for the lighting conditions and the color of the marker being used. The calibration window shows 6 sliders that control the minimum and maximum values for hue, saturation and value, as well as a live binary mask of the camera feed. The user adjusts these sliders until only the desired marker appears white and the rest of the image stays black.

Once the calibration is accepted, the selected HSV values are stored and used for marker tracking.

We chose a manual calibration over other methods because giving the user direct control over the HSV thresholds created a more reliable tracking across different cameras and lighting conditions, and it was also simpler to implement. This method also allows the adaptation of the application for different color markers without modifying the source code.

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

## Cursor Mapping & Preprocessing

The detected marker positions have to be converted from camera to screen coordinates to be able to be used to control the mouse. The cursor movement is based on the midpoint between two detected markers so first we calculate this midpoint. We then map it to the monitor resolution using linear interpolation.

At first we mapped the camera coordinates directly to the full screen but during testing we realized that moving your hand to the borders of the camera could be uncomfortable and the tracking would also become unstable.

To solve this and improve usability, we added a tracking margin. Instead of using the entire camera image, only a region marked by blue rectangle is considered for cursor movement. Positions outside of this region are clamped to the nearest boundary, allowing the user to reach the whole screen without having to move their hand far to either side.

Durging testing, the cursor had noticeable jitter, to improve this we added exponential smoothing to the cursor coordinates. After some testing we settled on a value of 0.25, with this value we got a good balance between jitter stability and responsive cursor movement.

To further improve the smoothnes and quality of the tracking, we added some image preprocessing. Before contour detection, a gaussian blur, erosion and dilation are applied to the mask to reduce high frequency noise and remove small artifacts.

## State Machine and Gestures

A state machine is the core of the gesture control system, managing transitions between six different states:

- idle: no markers are visible in the field of view and the system remains inactive.
- two_separate: The camera detects two separate markers. The system calculates the mathematical midpoint between them and maps it to screen coordinates to move the cursor smoothly.
- single_marker: Only one marker is detected. The resulting action depends on the previous state. Either a pinch is triggered or a right click is performed.
- pinched: The fingers merge to initiate a click event. If the pinch is held for at least five seconds, a double left click is triggered, otherwise a single left click is triggered.
- scroll: Three markers are detected. The midpoint of all three markers is calculated and vertical movement of this point is translated into mouse wheel scrolling.

## Scrolling Interaction

The paper uses the gesture with three visible markers to scrolling, where if the markers move downwards the system will scroll down and viceversa. 

We considered implementing this gesture using a touchscreen-style interaction, where the page would follow the user's finger movement directly since this way feels more natural. However, we decided to emulate the behavior of a standard desktop mouse wheel instead because this approach is consistent with the original paper and matches the expectation of creating a virtual mouse that behaves exactly like its original counterpart.

## Gesture Differentiation

There was an issue with distinguishing between two of the available actions: pinching with two fingers to create a single merged bounding box to perform a left single or double click (depending on how long the pinch is held) and showing only one single marker to perform a right mouse click. Since both of the actions only show one single marker there have been problems to tell which of both gestures is meant.

Initially, the system triggered a pinch whenever the count dropped to one marker because pinch_ready became True as soon as two markers appeared. This made it impossible to transition back to single_marker (right click) without triggering a false pinch. So, we introduced geometric validations:

- During the two_separate state, the system continuously tracks the distance (last_distance) and the final midpoint (last_midpoint) between the two fingers

- When we transition to the state single_marker, the system verifies if the distance was below a certain threshold and if the single marker lies close to last_midpoint

- When both of the conditions are true, we can enter the "pinched" state. Otherwise, a right click is performed because there was no merging of bounding boxes before and, we only have one single finger.

To not immediately trigger a pinch when two fingers are close, we implemented a feature proposed by the paper: We only trigger the pinch if the merged bounding box area becomes 20% of the original creation time bounding box area. However, during testing, using this feature felt unintuitive, and it was nearly impossible to shrink the size of the bounding box to only 20% of the original size. So, we decided to remove this functionality, so that the pinch is triggered as soon as the bounding boxes of the two fingers are merged. This proved to be much more intuitive.

The click duration threshold was also adjusted during testing. Requiring the user to hold a pinch for 5 seconds to perform a double click felt too slow and disrupted the workflow. This delay was significantly reduced to 1 second instead of 5, to create a much faster and more natural double-click gesture.

## Conclusion

The final implementation successfully reproduces the main concepts presented in [Design and Development of Hand Gesture Based
Virtual Mouse](https://doi.org/10.1109/ICASERT.2019.8934612). It supports real-time cursor movement, left and right mouse clicks, double click, and scrolling using colored finger markers and a standard webcam. We introduced several improvements beyond the original implementation to increase robustnes and usability, including a manual calibration mode, cursor smoothing, a tracking margin, and additional geometric validation for gesture recognition.

One of the challenges encountered during development was achieving reliable detection under different lighting conditions. Initially using fixed HSV thresholds produced inconsistent results. This issue was addressed by implementing a manual calibration mode allowing the user to adapt the HSV values to their current lighting conditions and the color of the marker.

Another challenge was distinguishing between gestures that produced the same number of detected markers. In particular, differentiating between a pinch and a right click initially resulted in false detections. This was solved by introducing geometric constraints based on the previous finger positions and distance between markers before they merged.

Some of the parameters proposed in the paper were removed after initial testing. Requiring the merged marker to shrink 20% of its original size before recognizing a pinch proved difficult to with consistency so it was removed. The original five-second delay for a double click was also reduced to one second to create a faster and more natural interaction. There was also an addition of cursor smoothing and a tracking margin to improve usability.

Although the implementation performs reliably under normal conditions, several limitations remain. The system depends on colored markers and cannot recognize bare hands. Tracking accuracy is heavily influenced by the lighting conditions, objects in the background with similar color can also cause and effect. The colored trackers must always be visible for the gesture recognition to work.

There is also potential for future improvements and extensions. The system could be expanded to support a wider range of interaction and more complex gestures than the predefined set. However, achieving a more advanced and reliable gesture recognition would likely require a more complex approach, such as integrating machine learning techniques or using additional hardware sensors.

In conclusion, we can say the this project demonstrates that a hand-gesture mouse can be implemented using only a webcam and standard computer vision techniques.
