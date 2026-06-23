from typing import Callable
from pydantic import BaseModel

class Move(BaseModel):
    tile: str
    from_x: int
    from_y: int
    speed_x: int
    speed_y: int
    progress: int = 0
    complete: bool = False
    finished: Callable = None

class Teleporter(BaseModel):
    x: int
    y: int
    target_x: int
    target_y: int

class Switch(BaseModel):
    x: int          
    y: int          
    wall_x: int     
    wall_y: int   
    activated: bool = False   

class Monster(BaseModel):
    x: int
    y: int
    direction: str
    move: Move = None

class Fireball(Monster):
   name: str = "fireball"

class Skeleton(Monster):
    name: str = "skeleton"
    dying: bool = False
    death_timer: int = 0

class Snake(Monster):
    name: str = "snake"
    dying: bool = False     
    death_timer: int = 0

class Giant(Monster):
    name: str = "giant"

class Projectile(BaseModel):
    x: int
    y: int
    direction: str
    projectile_type: str
    move: Move | None = None

class Dragon(Monster):
    name: str = "dragon"
    health: int = 100
    max_health: int = 100
    attack_timer: int = 100
    move_timer: int = 80

class Bullet(Monster):
    name: str = "bullet"
           