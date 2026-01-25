import numpy as np
import pygame as pg
pg.init()

#constants, init
G = 6.6743e-11
dt = 10000
SCALE = 1e9
FPS = 360
bodies = []

screen_width, screen_height = 720, 720
screen = pg.display.set_mode([screen_width, screen_height])
trails = pg.Surface((screen_width, screen_height))
trails.fill('black')
trails.set_alpha(5)

#classes, functions
class Body:
    def __init__(self, mass, pos, vel, acc, name, color):
        self.mass = mass
        self.pos = np.array(pos, dtype=float)
        self.vel = np.array(vel, dtype=float)
        self.acc = np.array(acc, dtype=float)
        self.name = name
        self.color = color
        bodies.append(self)

def gravity_force(body1, body2):
    r_vec = body2.pos-body1.pos #vector from body1 to body2
    r = np.linalg.norm(r_vec) #vector length
    F_mag = G * body1.mass * body2.mass / r**2 #newtons law of gravity
    direction = r_vec/r #unit vector from body1 to body2
    F = F_mag*direction #force vector from body1 to body2
    return F

def apply_acc(bodies):
    for body in bodies:
        body.acc = np.zeros(2) #reset acc

        for body2 in bodies:
            if body == body2:
                continue
            body.acc += gravity_force(body, body2) / body.mass # a = f/m

def update(bodies, dt):
    for body in bodies:
        body.vel += body.acc*dt
        body.pos += body.vel*dt

def draw_bodies(bodies):
    for body in bodies:
        x = body.pos[0]/SCALE + screen_width//2
        y = body.pos[1]/SCALE + screen_height//2
        r = 5
        pg.draw.circle(screen, body.color, (x, y), r)
        pg.draw.circle(trails, body.color, (x, y), 1)

    

#bodies
#source:
#https://www.milliganphysics.com/Physics/SSysData.htm
#or just made up :)

sun = Body(
    mass=2e30,
    pos=np.zeros(2),
    vel=np.zeros(2),
    acc=np.zeros(2),
    name='Sun',
    color='yellow'
)
earth = Body(
    mass=6e24, 
    pos=np.array([1.5e11, 0]), 
    vel = np.array([0, 25_000]), #30000
    acc=np.zeros(2), 
    name = 'Earth', 
    color="green"
)
planet3 = Body(
    mass=6e24, 
    pos=np.array([1.5e11, 1.5e11]), 
    vel = np.array([0, 20_000]),
    acc=np.zeros(2), 
    name = '3', 
    color="blue"
)
planet4 = Body(
    mass=6e28, 
    pos=np.array([-1e11, -1e11]), 
    vel = np.array([0, 25_000]),
    acc=np.zeros(2), 
    name = '4', 
    color="red"
)
#main pygame loop
clock = pg.time.Clock()
running = True
while running:
    screen.blit(trails, (0, 0))

    #events
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    
    #physics
    apply_acc(bodies)
    update(bodies, dt)

    draw_bodies(bodies)
    pg.display.flip()
    clock.tick(FPS)
