import cv2
import numpy as np
import time 
from pynput.mouse import Controller, Button
from tkinter import Tk

mouse = Controller()

# get screen width and height
root = Tk()
root.withdraw()
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
root.destroy()

cap = cv2.VideoCapture(0)

# default HSV values
lower_color = np.array([22, 17, 56])
upper_color = np.array([77, 255, 255])

# minimum area for markers to be detected as one 
MIN_AREA = 600
# percentage that merged area has to become relative to its original area for the fingers to be pinched
PINCH_RELATIVE_AREA = 0.6
# seconds after which double click is performed when fingers are pinched
PINCH_DOUBLECLICK_SECONDS = 1.0  # in the original paper, this was 5s, change it to your liking
PINCH_DISTANCE_THRESHOLD = 100  
MIDPOINT_DISTANCE_THRESHOLD = 60

mode = "menu"
trackbars_created = False

gesture_state = "idle"
pinch_ready = False
pinch_start_time = None
pinch_original_area = None
last_distance = 9999
last_midpoint = (0, 0)

# get the marker info 
def marker_info(contour):
    x, y, w, h = cv2.boundingRect(contour)
    return {
        "x": x, 
        "y": y,
        "w": w,
        "h": h,
        "cx": x + w // 2,
        "cy": y + h // 2,
        "bbox_area": w * h,
    }

# scales the position from the frame size to the monitor size
def to_screen(px, py, frame_w, frame_h):
    sx = int(px * screen_w / frame_w)
    sy = int(py * screen_h / frame_h)
    return sx, sy

def clear_pinch_timing():
    global pinch_start_time, pinch_original_area
    pinch_start_time = None
    pinch_original_area = None

def finalize_pinch():
    global pinch_ready

    if pinch_start_time is None:
        pinch_ready = False
        return 
    
    duration = time.time() - pinch_start_time

    if duration >= PINCH_DOUBLECLICK_SECONDS:
        # perform double click
        print("double click")
        mouse.click(Button.left, 2)
    else:
        # perform left mouse click
        print("left click")
        mouse.click(Button.left, 1)

    clear_pinch_timing()
    pinch_ready = False


while True:

    ret, frame = cap.read()

    if not ret:
        continue

    # Mirror the image so moving right moves the cursor right
    frame = cv2.flip(frame, 1)

    # Convert to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    key = cv2.waitKey(1) & 0xFF

    # main menu
    if mode == "menu":
        overlay = frame.copy()

        cv2.rectangle(overlay, (20, 20), (450, 200), (0,0,0), -1)

        frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)

        cv2.putText(
            frame,
            "Gesture Mouse",
            (50,60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255,255,255),
            2
        )

        cv2.putText(
            frame,
            "C - Calibrate Colors",
            (50,105),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255,255,255),
            2
        )

        cv2.putText(
            frame,
            "S - Start Mouse",
            (50,145),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255,255,255),
            2
        )

        cv2.putText(
            frame,
            "Q - Quit",
            (50,185),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255,255,255),
            2
        )

        #cv2.imshow("Gesture Mouse", frame)

        if key == ord('c'):
            mode = "calibration"

        elif key == ord('s'):
            mode = "mouse"

        elif key == ord('q'):
            break

    # Calibration
    elif mode == "calibration":
        if not trackbars_created:
            cv2.namedWindow("Calibration")

            cv2.createTrackbar("H Min","Calibration",0,179,lambda x:None)
            cv2.createTrackbar("H Max","Calibration",179,179,lambda x:None)

            cv2.createTrackbar("S Min","Calibration",0,255,lambda x:None)
            cv2.createTrackbar("S Max","Calibration",255,255,lambda x:None)

            cv2.createTrackbar("V Min","Calibration",0,255,lambda x:None)
            cv2.createTrackbar("V Max","Calibration",255,255,lambda x:None)

            trackbars_created = True

        # get slider values
        hmin = cv2.getTrackbarPos("H Min", "Calibration")
        hmax = cv2.getTrackbarPos("H Max", "Calibration")

        smin = cv2.getTrackbarPos("S Min", "Calibration")
        smax = cv2.getTrackbarPos("S Max", "Calibration")

        vmin = cv2.getTrackbarPos("V Min", "Calibration")
        vmax = cv2.getTrackbarPos("V Max", "Calibration")


        lower = np.array([hmin, smin, vmin])
        upper = np.array([hmax, smax, vmax])

        mask = cv2.inRange(hsv, lower, upper)

        # Instructions
        cv2.putText(
            mask,
            "ENTER - Accept",
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            255,
            2
        )

        cv2.putText(
            mask,
            "ESC - Return",
            (10, 55),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            255,
            2
        )

        cv2.imshow("Calibration", mask)

        # ENTER - save calibration
        if key == 13:
            lower_color = lower
            upper_color = upper

            cv2.destroyWindow("Calibration")

            trackbars_created = False

            mode = "menu"

        # ESC - cancel calibration
        if key == 27:
            cv2.destroyWindow("Calibration")

            trackbars_created = False

            mode = "menu"


    # Mouse Mode
    elif mode == "mouse":
        frame_h, frame_w = frame.shape[:2]

        mask = cv2.inRange(hsv, lower_color, upper_color)

        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # find contours 
        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        # set markers based on minimum area
        markers = [
            marker_info(c) for c in contours if cv2.contourArea(c) > MIN_AREA
        ]
        markers.sort(key=lambda m: m["x"])

        prev_state = gesture_state
        new_state = "idle"

        for i, marker in enumerate(markers):
            # create visible bounding box
            cv2.rectangle(
                frame, 
                (marker["x"], marker["y"]), 
                (marker["x"] + marker["w"], marker ["y"] + marker["h"]), 
                (0, 255, 0), 
                2
            )
            # create circle in the middle of bounding box
            cv2.circle(frame, (marker["cx"], marker["cy"]), 5, (0, 0, 255), -1)
            cv2.putText(
                frame,
                str(i + 1),
                (marker["x"], marker["y"] - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

        # two markers were detected
        if len(markers) == 2: 
            new_state = "two_separate"
            # pinch is ready to be performed
            pinch_ready = True

            if prev_state != "pinched":
                clear_pinch_timing()

            m1, m2 = markers[0], markers[1]

            mid_x = (m1["cx"] + m2["cx"]) // 2
            mid_y = (m1["cy"] + m2["cy"]) // 2

            sx, sy = to_screen(mid_x, mid_y, frame_w, frame_h)
            mouse.position = (sx, sy)

            # line between two bounding boxes
            cv2.line(frame, (m1["cx"], m1["cy"]), (m2["cx"], m2["cy"]), (255, 0, 0), 2)
            # circle in the middle of the line, tracker for the mouse pointer
            cv2.circle(frame, (mid_x, mid_y), 6, (255, 255, 0), -1)

            last_distance = np.hypot(m1["cx"] - m2["cx"], m1["cy"] - m2["cy"])
            last_midpoint = (mid_x, mid_y)

        # only one marker is detected
        elif len(markers) == 1:
            # if there were previously two markers 
            marker = markers[0]

            # distance to last measured midpoint
            dist_to_midpoint = np.hypot(marker["cx"] - last_midpoint[0], marker["cy"] - last_midpoint[1])

            # if last measured distance of the two markers is under some threshold, the two markers were merged 
            if pinch_ready and last_distance < PINCH_DISTANCE_THRESHOLD and dist_to_midpoint < MIDPOINT_DISTANCE_THRESHOLD: 
                new_state = "pinched"

                if pinch_original_area is None:
                    pinch_original_area = marker["bbox_area"]

                # if the area of the merged bounding box becomes 20% of its original size (at merging), then the pinch is detected
                # uncomment this to get back this functionality, but during testing, it proved to be nealry impossible to to shrink 
                # the size to 20% and it was much more intuitive to work wothout this feature.
                #if marker["bbox_area"] <= PINCH_RELATIVE_AREA * pinch_original_area:
                if pinch_start_time is None:
                    pinch_start_time = time.time()
            
            else:
                new_state = "single_marker"
                if prev_state != "single_marker" and prev_state != "pinched":
                    # perform right mouse click
                    mouse.click(Button.right)
                
                pinch_ready = False
                clear_pinch_timing()
        
        else: 
            new_state = "idle"
            pinch_ready = False
            clear_pinch_timing()

        gesture_state = new_state

        if prev_state == "pinched" and gesture_state != "pinched":
            finalize_pinch()


        cv2.putText(
            frame,
            "Mouse mode - ESC to return to menu",
            (30,50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,255,0),
            2
        )

    cv2.imshow("Gesture Mouse", frame)

    # Key Controls
    if key == 27 and mode == "mouse":
        mode = "menu"

    elif key == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()