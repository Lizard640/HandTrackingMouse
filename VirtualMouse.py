import cv2
import numpy as np
import HandTrackingModule as htm
import time
import math
import keyboard
import pyautogui

wCam, hCam = 640, 480

# Border parameters
border_size = 65  # Adjust the size of the border as needed
roi_width, roi_height = wCam - 2 * border_size, hCam - 2 * border_size
roi_x, roi_y = border_size, border_size

cap = cv2.VideoCapture(0)
actual_width = cap.get(3)
actual_height = cap.get(4)
print(f"Actual Camera Dimensions: {actual_width} x {actual_height}")

cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector(detectionCon=0.7)

# Screen dimensions
screen_width, screen_height = pyautogui.size()
print(f"Screen Dimensions: {screen_width} x {screen_height}")

# Smoothing parameters
smoothing_factor = 0.7
prev_cursor_x, prev_cursor_y = 0, 0

fps_update_interval = 10  # Display FPS every 10 frames
frame_count = 0

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    # Draw the border on the camera feed
    cv2.rectangle(img, (roi_x, roi_y), (roi_x + roi_width, roi_y + roi_height), (0, 255, 0), 2)

    if len(lmList[0]) != 0:

        x1, y1 = lmList[0][4][1], lmList[0][4][2]  # thumb
        x2, y2 = lmList[0][8][1], lmList[0][8][2]  # index
        x3, y3 = lmList[0][12][1], lmList[0][12][2]  # middle
        x6, y6 = lmList[0][16][1], lmList[0][16][2]  # ring
        x7, y7 = lmList[0][20][1], lmList[0][20][2]  # pinky

        x4, y4 = lmList[0][13][1], lmList[0][13][2]  # palm
        x5, y5 = lmList[0][9][1], lmList[0][9][2]  # palm

        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        zx, zy = (x1 + x3) // 2, (y1 + y3) // 2
        rx, ry = (x1 + x6) // 2, (y1 + y6) // 2
        px, py = (x1 + x7) // 2, (y1 + y7) // 2

        ax, ay = (x5 + x4) // 2, (y5 + y4) // 2

        # Check if the hand is within the defined border
        if roi_x < ax < roi_x + roi_width and roi_y < ay < roi_y + roi_height:
            # Invert the horizontal movement of the hand

            cursor_x = int(np.interp(ax, [roi_x - -30, roi_x + roi_width + -30], [screen_width, 0]))
            cursor_y = int(np.interp(ay, [roi_y - -30, roi_y + roi_height + -30], [0, screen_height]))

            # Smooth the cursor movement
            cursor_x = smoothing_factor * cursor_x + (1 - smoothing_factor) * prev_cursor_x
            cursor_y = smoothing_factor * cursor_y + (1 - smoothing_factor) * prev_cursor_y

            # Move the cursor to the smoothed position
            pyautogui.moveTo(int(cursor_x), int(cursor_y))

            # Update previous cursor position
            prev_cursor_x, prev_cursor_y = cursor_x, cursor_y

        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x3, y3), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x6, y6), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x7, y7), 10, (255, 0, 255), cv2.FILLED)

        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.line(img, (x1, y1), (x3, y3), (255, 0, 255), 3)
        cv2.line(img, (x1, y1), (x6, y6), (255, 0, 255), 3)
        cv2.line(img, (x1, y1), (x7, y7), (255, 0, 255), 3)

        cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (zx, zy), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (rx, ry), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (px, py), 10, (255, 0, 255), cv2.FILLED)

        length1 = math.hypot(x2 - x1, y2 - y1)
        length2 = math.hypot(x3 - x1, y3 - y1)
        length3 = math.hypot(x6 - x1, y6 - y1)
        length4 = math.hypot(x7 - x1, y7 - y1)

        if length1 < 30:
            cv2.circle(img, (cx, cy), 10, (0, 255, 255), cv2.FILLED)

            pyautogui.click()
            time.sleep(0.2)

        if length2 < 30:
            cv2.circle(img, (zx, zy), 10, (0, 255, 255), cv2.FILLED)

            pyautogui.click(button='right')
            time.sleep(0.2)

        if length3 < 35:
            cv2.circle(img, (rx, ry), 10, (0, 255, 255), cv2.FILLED)

            pyautogui.scroll(-100)

        if length4 < 35:
            cv2.circle(img, (px, py), 10, (0, 255, 255), cv2.FILLED)

            pyautogui.scroll(100)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 3)

    cv2.imshow("Img", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
