import numpy as np
from pydantic import BaseModel
import cv2

TILE_SIZE = 64

class Effect(BaseModel):

    x: int
    y: int
    countdown: int

    def draw(self, frame):
        pass

class RandomBlur(Effect):

    def draw(self, frame):
        random_tile = np.random.randint(0, 255, size=(TILE_SIZE, TILE_SIZE, 3), dtype=np.uint8)
        frame[self.y * TILE_SIZE: self.y * TILE_SIZE + TILE_SIZE,
            self.x * TILE_SIZE: self.x * TILE_SIZE + TILE_SIZE] = random_tile
        
class FadeIn(Effect):

    def draw(self, frame):
        tile = frame[self.y * TILE_SIZE: self.y * TILE_SIZE + TILE_SIZE,
            self.x * TILE_SIZE: self.x * TILE_SIZE + TILE_SIZE]
        tile[tile > (255 - self.countdown)] = 0
        frame[self.y * TILE_SIZE: self.y * TILE_SIZE + TILE_SIZE,
            self.x * TILE_SIZE: self.x * TILE_SIZE + TILE_SIZE] = tile
        
class ColorText(Effect):

    text: str

    def draw(self, frame):
        if self.countdown % 2 == 0:
            color = (255, 0, 255)
        else:
            color = (0, 255, 255)
        cv2.putText(frame,
            self.text,
            org=(self.y * TILE_SIZE, self.x * TILE_SIZE),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1.0,
            color=color,
            thickness=2,
        )
class DamageFlash(Effect):
    def draw(self, frame):
        x0 = self.x * TILE_SIZE
        y0 = self.y * TILE_SIZE
        if self.countdown % 2 == 0:   
            color = (0, 0, 180)       
            tile = frame[y0:y0+TILE_SIZE, x0:x0+TILE_SIZE].copy()
            cv2.rectangle(tile, (0, 0), (TILE_SIZE, TILE_SIZE), color, -1)
            alpha = 0.6  
            cv2.addWeighted(tile, alpha, frame[y0:y0+TILE_SIZE, x0:x0+TILE_SIZE], 1-alpha, 0,
                            frame[y0:y0+TILE_SIZE, x0:x0+TILE_SIZE])
            
class FlashEffect(Effect):
    def draw(self, frame):
        h, w = frame.shape[:2]
        intensity = int(255 * (self.countdown / 20))  
        intensity = min(255, max(0, intensity))
        white_overlay = np.full((h, w, 3), (255, 255, 255), dtype=np.uint8)
        alpha = intensity / 255.0
        cv2.addWeighted(white_overlay, alpha, frame, 1 - alpha, 0, frame)