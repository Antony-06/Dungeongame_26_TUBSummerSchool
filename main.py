"""
graphics engine for 2D games
"""
import os
import numpy as np
import cv2
from game import start_game, move_player, update, update_effects
from moves import Fireball, Skeleton, Snake, Giant, Projectile, Dragon  
from pygame import mixer
from cutscene import show_cutscene

TILE_PATH = os.path.split(__file__)[0] + '/tiles'

import cv2

files = [
    "gun.png",
    "laser.png",
    "bullet.png",
    "laser_bullet.png"]

for f in files:
    img = cv2.imread("tiles/" + f)
    img = cv2.resize(
        img,(32, 32))
    cv2.imwrite(
        "tiles/" + f,img)

# title of the game window
GAME_TITLE = "Dungeon Explorer"

# map keyboard keys to move commands
MOVES = {
    "a": "left",
    "d": "right",
    "w": "up",
    "s": "down",
}

#
# constants measured in pixels
#
SCREEN_SIZE_X, SCREEN_SIZE_Y = 1160, 960
TILE_SIZE = 64

def read_image(filename: str) -> np.ndarray:
    """
    Reads an image from the given filename and doubles its size.
    If the image file does not exist, an error is created.
    """
    img = cv2.imread(filename)  # sometimes returns None
    if img is None:
        raise IOError(f"Image not found: '{filename}'")
    img = np.kron(img, np.ones((2, 2, 1), dtype=img.dtype))  # double image size
    return img

def read_images():
    return {
        filename[:-4]: read_image(os.path.join(TILE_PATH, filename))
        for filename in os.listdir(TILE_PATH)
        if filename.endswith(".png")
    }


def draw_tile(frame, x, y, image, xbase=0, ybase=0):
    # calculate screen position in pixels
    xpos = xbase + x * TILE_SIZE
    ypos = ybase + y * TILE_SIZE
    # copy the image to the screen
    frame[ypos : ypos + TILE_SIZE, xpos : xpos + TILE_SIZE] = image

def draw_move(frame, move, images):
    draw_tile(frame, x=move.from_x, y=move.from_y, image=images[move.tile], xbase=move.progress * move.speed_x, ybase=move.progress * move.speed_y)
    move.progress += 1

def clean_moves(game, moves):
    result = []
    for m in moves:
        if m.progress * max(abs(m.speed_x), abs(m.speed_y)) < TILE_SIZE:
            result.append(m)
        else:
            m.complete = True
            if m.finished is not None:
                m.finished(game)
    return result

def is_player_moving(moves):
    return any([m for m in moves if m.tile == "player"])


def draw(game, images, moves):
    # initialize screen
    frame = np.zeros((SCREEN_SIZE_Y, SCREEN_SIZE_X, 3), np.uint8)

    SYMBOLS = {
    ".": "floor",
    "#": "wall",
    "f": "fountain",
    "x":"stairs_down",
    "€":"coin",
    "T":"trap",
    "K":"key",
    "D":"closed_door",
    "d":"open_door",
    "P":"potion",
    "S":"short_sword",
    "&":"shop"
    }

    for y, row in enumerate(game.current_level.level):
        for x, tile in enumerate(row):
            if tile in SYMBOLS:
                draw_tile(frame, x=x, y=y, image=images[SYMBOLS[tile]])

    # draw teleporters
    for t in game.current_level.teleporters:
        draw_tile(frame, x=t.x, y=t.y, image=images["teleporter"])

    # draw all monsters
    for m in game.current_level.monsters:

        if isinstance(m, Fireball):
            img = images["fireball"]
        elif isinstance(m, Skeleton):
            img = images["skeleton"]
        elif isinstance(m, Snake):
            img = images["snake"]
        elif isinstance(m, Giant):
            img = images["giant"]
        elif isinstance(m, Dragon):
            img = images["dragon"]
        else:
            continue
        if not m.move or m.move.complete:
            if isinstance(m, Dragon):
                dragon_img = cv2.resize(images["dragon"],(128, 128))

                x0 = m.x * TILE_SIZE
                y0 = m.y * TILE_SIZE

                frame[y0:y0+128,x0:x0+128] = dragon_img
            
            elif isinstance(m, Snake):
                if not m.dying:
                    draw_tile(frame, x=m.x, y=m.y, image=img)
            else:
                draw_tile(frame, x=m.x, y=m.y, image=img)
        if isinstance(m, (Snake, Skeleton)) and m.dying and m.death_timer > 0:
            x0 = m.x * TILE_SIZE
            y0 = m.y * TILE_SIZE
            if (m.death_timer % 2) == 0:
                color = (0, 0, 180)  # 暗红色
                tile = frame[y0:y0+TILE_SIZE, x0:x0+TILE_SIZE].copy()
                cv2.rectangle(tile, (0, 0), (TILE_SIZE, TILE_SIZE), color, -1)
                alpha = 0.6
                cv2.addWeighted(tile, alpha, frame[y0:y0+TILE_SIZE, x0:x0+TILE_SIZE], 1-alpha, 0,
                                frame[y0:y0+TILE_SIZE, x0:x0+TILE_SIZE])
       

    # draw player
    for m in game.current_level.monsters:
        if isinstance(m, Dragon):
            cv2.putText(
                frame,
                "ANCIENT DRAGON",
                (250, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255,255,255),2)
            frame[40:70, 250:850] = (50,50,50)
            bar_width = max(0,int(600 * m.health / m.max_health))
            frame[
                40:70,
                250:250+bar_width] = (0,0,255)

            cv2.putText(
            frame,
            f"{m.health}/{m.max_health}",
            (500,95),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255,255,255),2)

    while game.moves:
        moves.append(game.moves.pop())
    if not is_player_moving(moves):
        draw_tile(frame=frame, x=game.x, y=game.y, image=images["player"])
    
    # draw everything that moves
    for m in moves:
        draw_move(frame=frame, move=m, images=images)

    coin_img = images["coin"]
    coin_small = cv2.resize(coin_img, (32, 32))
    icon_x, icon_y = 1050, 93            
    frame[icon_y:icon_y+32, icon_x:icon_x+32] = coin_small
    
    cv2.putText(frame,
                str(game.coins),
                org=(980, 120),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=1.5,
                color=(255, 128, 128),
                thickness=3,
                )

    for p in game.projectiles:
        if (0 <= p.y < len(game.current_level.level)and 0<= p.x < len(game.current_level.level[0])):
            if "laser" in game.items:
                img = images["laser_bullet"]
            else:
                img = images["bullet"]
            draw_tile(
            frame,
            x=p.x,
            y=p.y,
            image=img)
    heart_img = images["heart"]        
    heart_small = cv2.resize(heart_img, (32, 32))
    start_x, start_y = 980, 150         
    for i in range(game.health):   
        x_pos = start_x + i * 32
        frame[start_y:start_y+32, x_pos:x_pos+32] = heart_small

    for i, item in enumerate(game.items):
        y = i // 2  # floor division: rounded down
        x = i % 2   # modulo: remainder of an integer division
        draw_tile(frame, xbase=980, ybase=210, x=x, y=y, image=images[item])

        # draw special effects
        # 受伤特效：玩家当前位置闪烁暗红色，持续 2 秒
    if game.damage_effect_timer > 0:
        game.damage_effect_timer -= 1
        # 每帧交替闪烁（奇数帧显示红色，偶数帧不显示）
        if (game.damage_effect_timer % 2) == 0:   # 可以调整闪烁频率
            x0 = game.x * TILE_SIZE
            y0 = game.y * TILE_SIZE
            color = (0, 0, 180)  # 暗红色 (BGR)
            # 复制玩家所在格子区域
            tile = frame[y0:y0+TILE_SIZE, x0:x0+TILE_SIZE].copy()
            # 绘制半透明红色矩形
            cv2.rectangle(tile, (0, 0), (TILE_SIZE, TILE_SIZE), color, -1)
            alpha = 0.6   # 透明度，数值越大红色越浓
            cv2.addWeighted(tile, alpha, frame[y0:y0+TILE_SIZE, x0:x0+TILE_SIZE], 1-alpha, 0,
                            frame[y0:y0+TILE_SIZE, x0:x0+TILE_SIZE])
            
         # draw all special effects (including FlashEffect)
    for e in game.effects:
        e.draw(frame)       

    # display complete image
    cv2.imshow(GAME_TITLE, frame)

    #return frame

def handle_keyboard(game):
    """keys are mapped to move commands"""
    key = chr(cv2.waitKey(1) & 0xFF)
    if key == "q":
        game.status = "exited"
    elif key == "j":

        if "gun" in game.items or "laser" in game.items:

            projectile_type = "bullet"

            if "laser" in game.items:
                projectile_type = "laser_bullet"

            game.projectiles.append(
                Projectile(
                    x=game.x,
                    y=game.y,
                    direction=game.facing,
                    projectile_type=projectile_type))

    return MOVES.get(key)

def show_victory_screen():

    img = cv2.imread("tiles/Victory.png")
    cv2.putText(
        img,
        "Press any key to continue...",
        (330, 760),     
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255,255,255),
        2)
    cv2.imshow("Victory", img)

    cv2.waitKey(0)

def main():
    images = read_images()
    if "shop" in images:
        images["shop"] = cv2.resize(images["shop"], (TILE_SIZE, TILE_SIZE))
    show_cutscene()
    mixer.init()
    mixer.music.load("gamemusic_v1.mp3")
    mixer.music.play(loops=-1)
    game = start_game()
    queued_move = None
    moves = []
    #fourcc = cv2.VideoWriter_fourcc(*"MP4V")
    #out = cv2.VideoWriter("myvideo.mp4", fourcc,
                      #60.0,   # frames per second
                      #(SCREEN_SIZE_X,SCREEN_SIZE_Y))

    while game.status == "running":
        draw(game, images, moves)
        #frame = draw(game, images, moves)
        #out.write(frame)
        moves = clean_moves(game, moves)
        update(game)
        update_effects(game)
        queued_move = handle_keyboard(game)
        # load and safe the game
        if not is_player_moving(moves) and queued_move:
            move_player(game, queued_move)
    #out.release()
    mixer.music.stop()

    if game.status == "victory":
        show_victory_screen()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
