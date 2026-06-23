import cv2
import numpy as np
import math
from pygame import mixer


def show_cutscene():

    img = cv2.imread("newtitle.png")

    mixer.init()
    mixer.music.load("gamemusic_v1.mp3")
    mixer.music.play(loops=-1)

    frame_count = 0

    while True:

        frame = img.copy()

        frame_count += 1

        alpha = (math.sin(frame_count * 0.08) + 1) / 2

        brightness = int(100 + alpha * 155)

        text_color = (
            0,
            0,
            brightness
        )

        # ==========================
        # 上下漂浮
        # ==========================

        offset_y = int(
            math.sin(frame_count * 0.05) * 5
        )

        text = "PRESS ANY KEY TO BEGIN YOUR JOURNEY"

        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 1.2
        thickness = 3

        text_size = cv2.getTextSize(
            text,
            font,
            scale,
            thickness
        )[0]

        x = 330
        y = 750

        # ==========================
        # 黑色描边
        # ==========================

        cv2.putText(
            frame,
            text,
            (x, y),
            font,
            scale,
            (0, 0, 0),
            8
        )

        # ==========================
        # 金色呼吸文字
        # ==========================

        cv2.putText(
            frame,
            text,
            (x, y),
            font,
            scale,
            text_color,
            thickness
        )

        cv2.imshow(
            "Dungeon Explorer - Title",
            frame
        )

        key = cv2.waitKey(16)

        if key != -1:
            break

    cv2.destroyWindow(
        "Dungeon Explorer - Title"
    )

    mixer.music.stop()
    