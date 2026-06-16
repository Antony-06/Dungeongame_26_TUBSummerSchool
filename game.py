"""
the Dungeon Explorer game logic
"""

MONSTER_MOVE_INTERVAL = 2   #稳定移动
frame_counter = 0

import random
from pydantic import BaseModel
from typing import Callable
from moves import Move, Teleporter, Switch, Monster, Fireball, Skeleton, Snake
from effects import Effect, RandomBlur, FadeIn, ColorText, DamageFlash,FlashEffect

#background settings
class Level(BaseModel):
    level: list[list[str]]
    teleporters: list[Teleporter] = []
    switches: list[Switch] = []
    monsters: list[Monster] = [] 
#player status
class DungeonGame(BaseModel):
    status: str = "running"
    x: int
    y: int
    coins: int = 0
    health: int = 5
    keys : int = 0
    short_sword: int = 0
    items: list[str] = []
    moves: list[Move] = []
    current_level: Level
    level_number: int = 0
    effects: list[Effect] = []
    damage_effect_timer: int = 0
def parse_level(level):
    return [list(row) for row in level]

LEVEL_ONE=Level(level=parse_level([   
    "###############",
    "#.S.....€....€#",
    "#..T..€..€....#",
    "#.K....T..€...#",
    "########DT##P.#",
    "#..€..##..#####",
    "#PK.......P#€x#",
    "#..€.##....#..#",
    "#.K€....T..#T.#",
    "#..Pf......#DD#",
    "#.€T.......#.P#",
    "###############",]),
    teleporters=[
    Teleporter(x=1, y=2, target_x=3, target_y=6), ],
    monsters=[
        Fireball(x=5, y=1, direction="right"),
        Fireball(x=5, y=5, direction="right"),
        Skeleton(x=1, y=5, direction="right"),
        Skeleton(x=7, y=2, direction="left"),
        Snake(x=5, y=8, direction="right")
    ]
)

LEVEL_TWO = Level(
    level=parse_level([
        "###############",
        "#........######",
        "#..P...€......#",
        "#..€.....######",
        "#.S..###.######",
        "#...T..€€######",
        "#€...P........#",
        "#.............#",
        "####..K.......#",
        "#€TD..........#",
        "########x######",
    ]),
    teleporters=[],
    monsters=[
        Fireball(x=3, y=5, direction="down"),
        Skeleton(x=8, y=4, direction="left"),
        Skeleton(x=2, y=5, direction="right"),
        Snake(x=3, y=2, direction="right")])

LEVELS = [LEVEL_ONE, LEVEL_TWO]

def reverse_direction(direction: str) -> str:
    if direction == "right":
        return "left"
    if direction == "left":
        return "right"
    if direction == "up":
        return "down"
    if direction == "down":
        return "up"
    return direction

def player_move_finished(game):
    #"outputs the coordinates of the player"
    print(game.x, game.y)

def move_player(game: DungeonGame, direction: str) -> None:
    """Things that happen when the player walks on stuff"""
    new_x, new_y = get_next_position(game.x, game.y, direction)

    if not (0 <= new_y < len(game.current_level.level) and 0 <= new_x < len(game.current_level.level[0])):
        return

    if game.current_level.level[new_y][new_x] == "€":
        game.current_level.level[new_y][new_x] = "."
        game.coins += 1

    if game.current_level.level[new_y][new_x] == "P":
        game.current_level.level[new_y][new_x] = "."
        if game.health < 5:
            game.health += 1

    if game.current_level.level[new_y][new_x] == "K" :
        game.items.append("key")
        game.current_level.level[new_y][new_x] = "."

    if game.current_level.level[new_y][new_x] == "S":
        game.current_level.level[new_y][new_x] = "."
        game.items.append("short_sword")

    tile = game.current_level.level[new_y][new_x]

    if tile in (".", "x", "T", "K","d"):
        if direction == "right":
            move = Move(tile="player", from_x=game.x, from_y=game.y, speed_x=2, speed_y=0, finished = player_move_finished)
                 
        elif direction == "left":
            move = Move(tile="player", from_x=game.x, from_y=game.y, speed_x=-2, speed_y=0,finished = player_move_finished)
            
        elif direction == "up":
            move = Move(tile="player", from_x=game.x, from_y=game.y, speed_x=0, speed_y=-2,finished = player_move_finished)
             
        elif direction == "down":
            move = Move(tile="player", from_x=game.x, from_y=game.y, speed_x=0, speed_y=2, finished = player_move_finished )

        game.moves.append(move)
        game.x = new_x
        game.y = new_y     

        if tile == "T":
            take_damage(game)

        check_teleporters(game)

        for m in game.current_level.monsters:
            check_collision(game, m)

    if game.x == 1 and game.y == 10:
        game.current_level.level[10][11] = "."
        move = Move(tile="wall", from_x=10, from_y=11, speed_x=2, speed_y=0)
        game.moves.append(move)

    if "key" in game.items and game.current_level.level[new_y][new_x] == "D":  # check whether there is a door
        game.items.remove("key") # key can be used once
        game.current_level.level[new_y][new_x] = "d" # replace the closed door by an open one

    if game.current_level.level[new_y][new_x] == "x":
        game.level_number += 1
        if game.level_number < len(LEVELS):
            game.current_level = LEVELS[game.level_number]
            game.x = 1
            game.y = 1
            game.moves.clear()
             
        else:
            game.status = "finished"
def check_teleporters(game):
    for t in game.current_level.teleporters:
        if game.x == t.x and game.y == t.y:
            game.effects.append(FlashEffect(x=0, y=0, countdown=20))
            game.x = t.target_x
            game.y = t.target_y
            target_tile =game.current_level.level[game.y][game.x]
           
            if target_tile == "€":
                game.coins += 1
                game.current_level.level[game.y][game.x] = "."
            elif target_tile == "K":
                game.items.append("key")
                game.current_level.level[game.y][game.x] = "."
            elif target_tile == "T":
                take_damage(game)
            break   

Position = tuple[int, int]

def get_next_position(x: int, y: int, direction: str) -> Position:
    if direction == "right":
        x += 1
    elif direction == "left":
        x -= 1
    elif direction == "up":
        y -= 1
    elif direction == "down":
        y += 1
    return x,y
    

def start_game():
    game = DungeonGame(
    x=1,
    y=1,
    current_level=LEVELS[0],
    level_number=0)
    game.effects.append(RandomBlur(x=8, y=1, countdown=500))
    return game
        
    


def take_damage(game, amount=1):
    game.health -= amount
    game.damage_effect_timer = 120
    if game.health <= 0:
        game.status = "game over"

def move_fireball(game: DungeonGame, fireball: Fireball):
    new_x, new_y = get_next_position(fireball.x, fireball.y, fireball.direction)
    tile = game.current_level.level[new_y][new_x]
    if tile in (".", "€", "K", "d","S"):
        old_x, old_y = fireball.x, fireball.y

        fireball.x = new_x
        fireball.y = new_y

        speed_x, speed_y = 0, 0
        if fireball.direction == "right":
            speed_x = 2
        elif fireball.direction == "left":
            speed_x = -2
        elif fireball.direction == "up":
            speed_y = -2
        elif fireball.direction == "down":
            speed_y = 2

        move = Move(
            tile="fireball",
            from_x=old_x, from_y=old_y,
            speed_x=speed_x, speed_y=speed_y
        )
        game.moves.append(move)
        fireball.move = move

    else:
        fireball.direction = reverse_direction(fireball.direction)

def move_skeleton(game, skeleton):
    skeleton.direction = random.choice(["up", "down", "left", "right"])
    new_x, new_y = get_next_position(skeleton.x, skeleton.y, skeleton.direction)
    tile = game.current_level.level[new_y][new_x]
    if tile in (".", "€", "K", "d","S"):
        old_x, old_y = skeleton.x, skeleton.y

        skeleton.x = new_x
        skeleton.y = new_y

        speed_x, speed_y = 0, 0
        if skeleton.direction == "right":
            speed_x = 2
        elif skeleton.direction == "left":
            speed_x = -2
        elif skeleton.direction == "up":
            speed_y = -2
        elif skeleton.direction == "down":
            speed_y = 2

        move = Move(
            tile="skeleton",
            from_x=old_x, from_y=old_y,
            speed_x=speed_x, speed_y=speed_y
        )
        game.moves.append(move)
        skeleton.move = move

def move_snake(game: DungeonGame, snake: Snake):
    snake.direction = random.choice(["up", "down", "left", "right"])
    new_x, new_y = get_next_position(snake.x, snake.y, snake.direction)
    tile = game.current_level.level[new_y][new_x]
    if tile in (".", "€", "K", "d", "D","T"):
        old_x, old_y = snake.x, snake.y
        snake.x = new_x
        snake.y = new_y

        speed_x, speed_y = 0, 0
        if snake.direction == "right":
            speed_x = 1
        elif snake.direction == "left":
            speed_x = -1
        elif snake.direction == "up":
            speed_y = -1
        elif snake.direction == "down":
            speed_y = 1
        move = Move(
            tile="snake",   
            from_x=old_x, from_y=old_y,
            speed_x=speed_x, speed_y=speed_y
        )
        game.moves.append(move)
        snake.move = move

def update(game):
    global frame_counter
    frame_counter += 1
    if frame_counter < MONSTER_MOVE_INTERVAL:
        return
    frame_counter = 0

    new_monsters = []
    for m in game.current_level.monsters:
        if isinstance(m, Fireball):
            if m.move is None or m.move.complete:
                move_fireball(game, m)
                check_collision(game, m)
            new_monsters.append(m)
        elif isinstance(m, Skeleton):
            if m.move is None or m.move.complete:
                move_skeleton(game, m)
                check_collision(game, m)
            new_monsters.append(m)
        elif isinstance(m, Snake):
            if m.dying:
                m.death_timer -= 1
                if m.death_timer > 0:
                    new_monsters.append(m)
            else:
                if not m.move or m.move.complete:
                    move_snake(game, m)
                    check_collision(game, m)
                new_monsters.append(m)
        else:
            new_monsters.append(m)
    game.current_level.monsters = new_monsters

def check_collision(game, monster):
    if isinstance(monster, Snake) and monster.dying:
        return

    if monster.x == game.x and monster.y == game.y:
        if isinstance(monster, Snake):
            if "short_sword" in game.items:
                if not monster.dying:  
                    monster.dying = True
                    monster.death_timer = 60   
                    game.items.remove("short_sword")
            else:
                take_damage(game, amount=2)
        else:   
            take_damage(game, amount=1)
def update_effects(game):
    new_effects = []
    for e in game.effects:
        e.countdown -= 1
        if e.countdown > 0:
            new_effects.append(e)
    game.effects = new_effects
