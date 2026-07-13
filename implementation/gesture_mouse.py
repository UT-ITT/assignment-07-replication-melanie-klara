import cv2
import numpy as np


cap = cv2.VideoCapture(0)

# default HSV values
lower_color = np.array([22, 17, 56])
upper_color = np.array([77, 255, 255])

mode = "menu"
trackbars_created = False

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

        mask = cv2.inRange(hsv, lower_color, upper_color)

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        if contours:
            largest = max(contours, key=cv2.contourArea)

            if cv2.contourArea(largest) > 300:
                x, y, w, h = cv2.boundingRect(largest)

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                cx = x + w // 2
                cy = y + h // 2

                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

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