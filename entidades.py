import pygame
from config import GREEN_BRIGHT, GREEN_DARK, HEAD_COLOR, WHITE, BLACK, ROWS

class Cube:
    W = 500 // ROWS   # tamaño de celda

    def __init__(self, start, dirnx=1, dirny=0, color=GREEN_BRIGHT):
        self.pos   = start
        self.dirnx = dirnx
        self.dirny = dirny
        self.color = color

    def move(self, dirnx, dirny):
        self.dirnx = dirnx
        self.dirny = dirny
        self.pos   = (self.pos[0] + self.dirnx, self.pos[1] + self.dirny)

    def draw(self, surface, eyes=False, index=0):
        dis = self.W
        i, j = self.pos
        px, py = i * dis, j * dis
        if eyes:
            pygame.draw.rect(surface, HEAD_COLOR, (px+1, py+1, dis-2, dis-2), border_radius=5)
            pygame.draw.rect(surface, WHITE,       (px+1, py+1, dis-2, dis-2), 2, border_radius=5)
            pygame.draw.circle(surface, BLACK, (px+6,     py+7), 3)
            pygame.draw.circle(surface, BLACK, (px+dis-7, py+7), 3)
        else:
            color = GREEN_BRIGHT if index % 2 == 0 else GREEN_DARK
            pygame.draw.rect(surface, color, (px+2, py+2, dis-4, dis-4), border_radius=4)


class Snake:
    def __init__(self, color, pos):
        self.color = color
        self.head = Cube(pos)
        self.body = [self.head]
        self.turns = {}
        self.dirnx = 0
        self.dirny = 0
        self.last_dir = 1   

    def move(self, events=None):
        if events is None:
            events = []
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and self.dirnx != 1:
                    self.dirnx, self.dirny = -1,  0
                    self.last_dir = 2
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
                elif event.key == pygame.K_RIGHT and self.dirnx != -1:
                    self.dirnx, self.dirny =  1,  0
                    self.last_dir = 3
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
                elif event.key == pygame.K_UP and self.dirny != 1:
                    self.dirnx, self.dirny =  0, -1
                    self.last_dir = 0
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
                elif event.key == pygame.K_DOWN and self.dirny != -1:
                    self.dirnx, self.dirny =  0,  1
                    self.last_dir = 1
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

        for i, c in enumerate(self.body):
            p = c.pos[:]
            if p in self.turns:
                turn = self.turns[p]
                c.move(turn[0], turn[1])
                if i == len(self.body) - 1:
                    self.turns.pop(p)
            else:
                c.move(c.dirnx, c.dirny)

    def reset(self, pos):
        self.head     = Cube(pos)
        self.body     = [self.head]
        self.turns    = {}
        self.dirnx    = 0
        self.dirny    = 1
        self.last_dir = 1

    def addCube(self):
        tail   = self.body[-1]
        dx, dy = tail.dirnx, tail.dirny
        if   dx ==  1 and dy == 0: self.body.append(Cube((tail.pos[0]-1, tail.pos[1])))
        elif dx == -1 and dy == 0: self.body.append(Cube((tail.pos[0]+1, tail.pos[1])))
        elif dx == 0  and dy == 1: self.body.append(Cube((tail.pos[0],   tail.pos[1]-1)))
        elif dx == 0  and dy ==-1: self.body.append(Cube((tail.pos[0],   tail.pos[1]+1)))
        self.body[-1].dirnx = dx
        self.body[-1].dirny = dy

    def draw(self, surface):
        for i, c in enumerate(self.body):
            c.draw(surface, eyes=(i == 0), index=i)
