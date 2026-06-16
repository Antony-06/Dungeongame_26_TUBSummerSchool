import cv2
import numpy as np

WHITE =255, 255, 255
BLUE = 255, 0, 0
RED = 0, 0, 255

while chr(cv2.waitKey(1) & 0xFF) != "q":
    frame = np.zeros((400, 600, 3), np.uint8)
    frame[:, :] = WHITE
    frame[150:250, :] = RED
    frame[:, 150:250] = RED

    cv2.imshow("title", frame)

cv2.destroyAllWindows