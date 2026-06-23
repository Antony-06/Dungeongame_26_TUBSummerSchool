"""
the Dungeon Explorer game logic
"""

MONSTER_MOVE_INTERVAL = 2  
frame_counter = 0

import random
from pydantic import BaseModel
from typing import Callable
from moves import Move, Teleporter, Switch, Monster, Fireball, Skeleton, Snake, Giant, Projectile,Dragon, Bullet
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
    facing: str = "right"
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
    projectiles: list[Projectile] = []
    bullets: list[Bullet] = []

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
    "#.€T&......#.P#",
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
        "#..€.....##..##",
        "#....###.....##",
        "#...T..€€##..##",
        "#€...P......€.#",
        "#.....#D#.....#",
        "#..€€.#.#..P..#",
        "####.K#K#D#...#",
        "#€TD..#.#.#..&#",
        "#########x#####",
    ]),
    teleporters=[],
    monsters=[
        Fireball(x=3, y=5, direction="down"),
        Skeleton(x=8, y=4, direction="left"),
        Skeleton(x=2, y=5, direction="right"),
        Skeleton(x=7,y=9, direction = "up"),
        Snake(x=3, y=2, direction="right"),
        Giant(x=11,y=3, direction = "right")])

def generate_random_level():

    width = 15
    height = 12

    level = []

    for y in range(height):

        row = []

        for x in range(width):

            if (
                x == 0
                or x == width - 1
                or y == 0
                or y == height - 1
            ):
                row.append("#")
            else:
                row.append(".")

        level.append(row)

    level[1][1] = "."

    # 随机墙
    for _ in range(25):

        x = random.randint(1, width - 2)
        y = random.randint(1, height - 2)

        level[y][x] = "#"

    # 随机金币
    for _ in range(12):

        x = random.randint(1, width - 2)
        y = random.randint(1, height - 2)

        if level[y][x] == ".":
            level[y][x] = "€"

    # 随机陷阱
    for _ in range(8):

        x = random.randint(1, width - 2)
        y = random.randint(1, height - 2)

        if level[y][x] == ".":
            level[y][x] = "T"

    # 商店
    while True:
        x = random.randint(1, width - 2)
        y = random.randint(1, height - 2)

        if level[y][x] == ".":
            level[y][x] = "&"
            break
    # 终点
        # 终点：确保出口及其四周畅通
    exit_x = width - 2
    exit_y = height - 2

    # 1. 清空出口位置（防止被随机墙占据）
    level[exit_y][exit_x] = '.'

    # 2. 清空四个邻居（上、下、左、右）
    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        nx, ny = exit_x + dx, exit_y + dy
        # 确保不越界（其实不会越界，因为出口在内部）
        if 0 <= ny < height and 0 <= nx < width:
            if level[ny][nx] == '#':
                level[ny][nx] = '.'

    # 3. 放置出口
    level[exit_y][exit_x] = 'x'

    return level

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
    "#.€T&......#.P#",
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
        "#..€.....##..##",
        "#.S..###.....##",
        "#...T..€€##..##",
        "#€...P......€.#",
        "#.....#D#.....#",
        "#..€€.#.#..P..#",
        "####.K#K#D#...#",
        "#€TD..#.#.#..&#",
        "#########x#####",
    ]),
    teleporters=[],
    monsters=[
        Fireball(x=3, y=5, direction="down"),
        Skeleton(x=8, y=4, direction="left"),
        Skeleton(x=2, y=5, direction="right"),
        Skeleton(x=7,y=9, direction = "up"),
        Snake(x=3, y=2, direction="right"),
        Giant(x=11,y=3, direction = "right")])

def generate_random_levels(n):

    levels = []

    for i in range(n):
        levels.append(Level(level=generate_random_level(),
                            teleporters=[],
                            monsters=[Skeleton(x=6,y=6,direction="left"),
                            Snake(x=10,y=4,direction="right"),
                            Giant(x=8,y=8,direction="left")]))
    return levels

LEVEL_PRE_BOSS = Level(
    level=parse_level([
        "###############",
        "#.............#",
        "#.............#",
        "#.............#",
        "#......P......#",
        "#.....P&P.....#",
        "#......P......#",
        "#.............#",
        "#.............#",
        "#.............#",
        "#............x#",
        "###############",
    ]),
    teleporters=[],
    monsters=[])

LEVEL_BOSS = Level(
    level=parse_level([
        "###############",
        "#.............#",
        "#.............#",
        "#.............#",
        "#.............#",
        "#.............#",
        "#.............#",
        "#.............#",
        "#.............#",
        "#.............#",
        "#.............#",
        "###############",
    ]),
    teleporters=[],
    monsters=[Dragon(x=6, y=4, direction="left")])

RANDOM_LEVEL_COUNT = 2
LEVELS = [LEVEL_ONE,LEVEL_TWO]
LEVELS.extend(generate_random_levels(RANDOM_LEVEL_COUNT))
LEVELS.append(LEVEL_PRE_BOSS)
LEVELS.append(LEVEL_BOSS)

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
    game.facing = direction
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
    #open the door immediately with a key and step in at the same time
    if tile == "D" and "key" in game.items:
        game.items.remove("key")
        game.current_level.level[new_y][new_x] = "d"
        tile = "d"

    if tile in (".", "x", "T", "K","d","&"):
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

        if game.current_level.level[game.y][game.x] == "&":
            from shop import visit_shop
            visit_shop(game)

    if game.x == 1 and game.y == 10:
        game.current_level.level[10][11] = "."
        move = Move(tile="wall", from_x=10, from_y=11, speed_x=2, speed_y=0)
        game.moves.append(move)

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

def move_projectile(projectile):

    if projectile.direction == "left":
        projectile.x -= 1

    elif projectile.direction == "right":
        projectile.x += 1

    elif projectile.direction == "up":
        projectile.y -= 1

    elif projectile.direction == "down":
        projectile.y += 1

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

def move_giant(game: DungeonGame, giant: Giant):
    giant.direction = random.choice(["up", "down", "left", "right"])
    new_x, new_y = get_next_position(giant.x, giant.y, giant.direction)
    tile = game.current_level.level[new_y][new_x]
    if tile in (".", "€", "K", "d", "D","T"):
        old_x, old_y = giant.x, giant.y
        giant.x = new_x
        giant.y = new_y

        speed_x, speed_y = 0, 0
        if giant.direction == "right":
            speed_x = 1
        elif giant.direction == "left":
            speed_x = -1
        elif giant.direction == "up":
            speed_y = -1
        elif giant.direction == "down":
            speed_y = 1
        move = Move(
            tile="giant",   
            from_x=old_x, from_y=old_y,
            speed_x=speed_x, speed_y=speed_y
        )
        game.moves.append(move)
        giant.move = move

def move_dragon(game, dragon):

    direction = random.choice(
        ["up", "down", "left", "right"]
    )

    new_x, new_y = get_next_position(
        dragon.x,
        dragon.y,
        direction
    )

    level = game.current_level.level

    if (
        level[new_y][new_x] == "."
        and level[new_y][new_x + 1] == "."
        and level[new_y + 1][new_x] == "."
        and level[new_y + 1][new_x + 1] == "."
    ):

        dragon.x = new_x
        dragon.y = new_y

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

        elif isinstance(m, Skeleton):

                if m.dying:
                    m.death_timer -= 1
                    if m.death_timer > 0:
                        new_monsters.append(m)

                else:
                    if not m.move or m.move.complete:
                        move_skeleton(game, m)
                        check_collision(game, m)

                    new_monsters.append(m)

        elif isinstance(m, Giant):
            if m.move is None or m.move.complete:
                move_giant(game, m)
                check_collision(game, m)

            new_monsters.append(m)

        elif isinstance(m, Dragon):
            m.move_timer -= 1
            m.attack_timer -= 1
            if m.move_timer <= 0:
                move_dragon(game, m)
                m.move_timer = 60
            if m.attack_timer <= 0:
                direction = random.choice(["up", "down", "left", "right"])

                game.current_level.monsters.append(Fireball(x=m.x,y=m.y, direction=direction))

                m.attack_timer = 100

            new_monsters.append(m)

        else:
            new_monsters.append(m)
    game.current_level.monsters = new_monsters
    
    new_projectiles = []

    for p in game.projectiles:
        move_projectile(p)
        hit_dragon = False
        for m in game.current_level.monsters:
            if isinstance(m, Dragon):
                if (m.x <= p.x <= m.x + 1 and m.y <= p.y <= m.y + 1):
                    damage = 1
                    if p.projectile_type == "laser_bullet":
                        damage = 5
                    m.health = max(0, m.health - damage)
                if m.health <= 0:
                    game.status = "victory"
                    hit_dragon = True

                    break

        if (0 <= p.y < len(game.current_level.level) and 0 <= p.x < len(game.current_level.level[0]) and not hit_dragon and game.current_level.level[p.y][p.x] != "#"):
            new_projectiles.append(p)
def check_collision(game, monster):
    if isinstance(monster, Dragon):
        if (monster.x <= game.x <= monster.x + 1
        and
        monster.y <= game.y <= monster.y + 1):
            take_damage(game, amount=1)

        return
    if isinstance(monster, Snake) and monster.dying:
        return
    
    if isinstance(monster, Skeleton) and monster.dying:
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

        elif isinstance(monster, Skeleton):
            if "bow" in game.items:
                if not monster.dying:
                    monster.dying = True
                    monster.death_timer = 60

            else:
                take_damage(game, amount=1)

        elif isinstance(monster, Giant):
            if "armor" not in game.items:
                take_damage(game, amount=3)
            return
        else:   
            take_damage(game, amount=1)
def update_effects(game):
    new_effects = []
    for e in game.effects:
        e.countdown -= 1
        if e.countdown > 0:
            new_effects.append(e)
    game.effects = new_effects
