import os
import cv2
import numpy as np
import random

TILE_PATH = os.path.join(os.path.dirname(__file__), "tiles")

SHOP_TITLE = "Dungeon Shop"

SCREEN_SIZE_X = 1100
SCREEN_SIZE_Y = 800


def read_image(filename, size=(64, 64)):
    img = cv2.imread(filename)

    if img is None:
        raise IOError(f"Cannot find image: {filename}")

    return cv2.resize(img, size)


def read_images():

    images = {}

    for filename in os.listdir(TILE_PATH):

        if filename.endswith(".png"):

            name = filename[:-4]

            images[name] = cv2.imread(
                os.path.join(TILE_PATH, filename)
            )

    return images


def visit_shop(game):

    images = read_images()

    # ==========================
    # Seller
    # ==========================

    seller = read_image(
        os.path.join(TILE_PATH, "shop_seller.png"),
        (260, 260)
    )

    # ==========================
    # Shop Items
    # ==========================

    shop_items = [
        {"name": "bow",
         "cost": 10,
         "desc": "Kill skeletons instantly"},
        
        {"name": "potion",
         "cost": 5,
         "desc": "Restore 1 HP"},
            
        {"name": "armor",
         "cost": 8,
         "desc": "Protect against Giants"},

        {"name": "gun",
         "cost": 15,
         "desc": "Fight against dragon"},

        {"name": "laser",
         "cost": 25,
         "desc": "Better fight against dragon"}]

    merchant_quotes = [
        "Take a look, traveler.",
        "The dungeon is unforgiving.",
        "Need supplies for your journey?",
        "Gold speaks louder than words.",
        "I've got what you need.",
        "A wise adventurer shops first.",
        "Careful down there...",
        "Many entered. Few returned."]

    merchant_quote = random.choice(
    merchant_quotes)

    selected = 0

    feedback = "Welcome, traveler."
    feedback_color = (255, 255, 255)

    while True:

        frame = np.zeros(
            (SCREEN_SIZE_Y, SCREEN_SIZE_X, 3),
            dtype=np.uint8
        )

        # Background

        frame[:] = (35, 25, 20)

        # ==========================
        # Title
        # ==========================

        cv2.putText(
            frame,
            "DUNGEON SHOP",
            (250, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 215, 255),
            3
        )

        # ==========================
        # Seller Area
        # ==========================

        frame[120:380, 40:300] = seller

        cv2.putText(
            frame,
            "Merchant",
            (85, 410),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (200, 220, 255),
            2)
        # Merchant dialogue box

        cv2.rectangle(
        frame,
        (20, 430),
        (360, 510),
        (60, 50, 40),
        -1)

        cv2.rectangle(
        frame,
        (20, 430),
        (360, 510),
        (180, 160, 120),
        2)

        cv2.putText(
        frame,
        merchant_quote,
        (30, 465),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 220, 180),
        1)

        # ==========================
        # Shop Items
        # ==========================

        start_x = 430
        start_y = 150

        for i, item in enumerate(shop_items):

            y = start_y + i * 110

            # Highlight selected item

            if i == selected:

                cv2.rectangle(
                    frame,
                    (400, y - 45),
                    (980, y + 40),
                    (70, 70, 70),
                    -1
                )

                color = (0, 255, 0)

            else:

                color = (220, 220, 220)

            # Draw icon

            if item["name"] in images:

                icon = cv2.resize(
                    images[item["name"]],
                    (48, 48)
                )

                frame[
                    y - 35:y + 13,
                    start_x:start_x + 48
                ] = icon

            # Name

            cv2.putText(
                frame,
                item["name"].upper(),
                (start_x + 70, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                color,
                2
            )

            # Cost

            cv2.putText(
                frame,
                f"{item['cost']} coins",
                (start_x + 220, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2
            )

            # Description

            cv2.putText(
                frame,
                item["desc"],
                (start_x + 70, y + 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (180, 180, 180),
                1
            )

        # ==========================
        # Bottom Panel
        # ==========================

        cv2.rectangle(
            frame,
            (0, 630),
            (1100, 800),
            (20, 20, 20),
            -1
        )

        cv2.putText(
            frame,
            f"Coins: {game.coins}",
            (30, 700),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"HP: {game.health}/5",
            (250, 700),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            "W/S = Select",
            (30, 740),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (220, 220, 220),
            2
        )

        cv2.putText(
            frame,
            "SPACE = Buy",
            (250, 665),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (220, 220, 220),
            2
        )

        cv2.putText(
            frame,
            "E = Exit",
            (500, 665),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (220, 220, 220),
            2
        )

        # Feedback

        cv2.putText(
            frame,
            feedback,
            (30, 780),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            feedback_color,
            2
        )

        cv2.imshow(SHOP_TITLE, frame)

        key = cv2.waitKey(0) & 0xFF

        # ==========================
        # Exit
        # ==========================

        if key in [ord("e"), ord("E")]:

            break

        # ==========================
        # Up
        # ==========================

        elif key in [ord("w"), ord("W")]:

            selected = (
                selected - 1
            ) % len(shop_items)

        # ==========================
        # Down
        # ==========================

        elif key in [ord("s"), ord("S")]:

            selected = (
                selected + 1
            ) % len(shop_items)

        # ==========================
        # Buy
        # ==========================

        elif key == 32:

            item = shop_items[selected]

            # Unique items

            if (
                item["name"] != "potion"
                and item["name"] in game.items
            ):

                feedback = random.choice([
                    "You already own one.",
                    "One is enough.",
                    "No need for another.",
                    "That item is already yours."
                ])

                feedback_color = (0, 200, 255)

                continue

            # Not enough coins

            if game.coins < item["cost"]:

                feedback = random.choice([
                    "Come back with more coins.",
                    "No credit in this shop.",
                    "Coins first, goods later.",
                    "That costs more than you have."
                    ])

                feedback_color = (0, 0, 255)

                continue

            # Purchase

            game.coins -= item["cost"]

            if item["name"] == "potion":

                if game.health < 5:

                    game.health += 1

                feedback = random.choice([
                    "You look healthier.",
                    "That should help.",
                    "A little healing goes far.",
                    "+1 HP restored!"
                ])
            else:

                game.items.append(
                    item["name"]
                )

                feedback = random.choice([
                    "Excellent choice.",
                    "You'll need that.",
                    "A worthy investment.",
                    "May it serve you well."
                ])

            feedback_color = (0, 255, 0)

    cv2.destroyWindow(SHOP_TITLE)