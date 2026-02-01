import numpy as np
import pygame as pg
pg.init()

#constants, init

G = 6.6743e-11
dt = 86400 #seconds between frames
SCALE = 1.4e10
FPS = 360
bodies = []
ZOOM_SPEED = 1/(5)
MIN_SCALE = 1e9
MAX_SCALE = 1.4e10


font = pg.font.SysFont("Arial", 20)
screen_width, screen_height = 720, 720
screen = pg.display.set_mode([screen_width, screen_height])
trails = pg.Surface((screen_width, screen_height))
trails.fill('black')
#trails.set_alpha(5)
sim_time = 0 #seconds

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
        name_surf = font.render(body.name, True, (255,255,255))
        screen.blit(name_surf, (x+8, y-8))


    


# Sun
sun = Body(
    mass=1.989e30,
    pos=np.array([0.0, 0.0]),
    vel=np.array([0.0, 0.0]),
    acc=np.zeros(2),
    name='Sun',
    color=(255, 255, 0)
)

# Mercury
mercury = Body(
    mass=3.3e23,
    pos=np.array([5.79e10, 0.0]),
    vel=np.array([0.0, 47_400]),
    acc=np.zeros(2),
    name='Mercury',
    color=(150, 150, 150)
)

# Venus
venus = Body(
    mass=4.87e24,
    pos=np.array([1.082e11, 0.0]),
    vel=np.array([0.0, 35_020]),
    acc=np.zeros(2),
    name='Venus',
    color=(255, 200, 150)
)

# Earth
earth = Body(
    mass=5.97e24,
    pos=np.array([1.496e11, 0.0]),
    vel=np.array([0.0, 29_780]),
    acc=np.zeros(2),
    name='Earth',
    color=(0, 150, 255)
)

# Mars
mars = Body(
    mass=6.42e23,
    pos=np.array([2.279e11, 0.0]),
    vel=np.array([0.0, 24_130]),
    acc=np.zeros(2),
    name='Mars',
    color=(255, 100, 50)
)

# Jupiter
jupiter = Body(
    mass=1.898e27,
    pos=np.array([7.785e11, 0.0]),
    vel=np.array([0.0, 13_070]),
    acc=np.zeros(2),
    name='Jupiter',
    color=(255, 150, 100)
)

# Saturn
saturn = Body(
    mass=5.683e26,
    pos=np.array([1.433e12, 0.0]),
    vel=np.array([0.0, 9_680]),
    acc=np.zeros(2),
    name='Saturn',
    color=(255, 220, 180)
)

# Uranus
uranus = Body(
    mass=8.681e25,
    pos=np.array([2.877e12, 0.0]),
    vel=np.array([0.0, 6_800]),
    acc=np.zeros(2),
    name='Uranus',
    color=(100, 200, 255)
)

# Neptune
neptune = Body(
    mass=1.024e26,
    pos=np.array([4.503e12, 0.0]),
    vel=np.array([0.0, 5_430]),
    acc=np.zeros(2),
    name='Neptune',
    color=(50, 100, 255)
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
        #zoom
        elif event.type == pg.MOUSEWHEEL:
            if event.y > 0:
                SCALE *= ZOOM_SPEED
            elif event.y < 0:
                SCALE /= ZOOM_SPEED
            SCALE = max(MIN_SCALE, min(MAX_SCALE, SCALE))
            trails.fill('black') #clear trails
    #physics
    apply_acc(bodies)
    update(bodies, dt)

    #timer
    sim_time += dt
    days = (sim_time // 86400 ) % 365
    hours = (sim_time % 86400) // 3600
    minutes = (sim_time % 3600) // 60
    seconds = sim_time % 60
    years = sim_time//86400//365
    timer_text = f"{years}y {days}d {hours:02}h {minutes:02}m {seconds:02}s"
    text_surf = font.render(timer_text, True, (255, 255, 255))

    timer_rect = pg.Rect(
        screen_width - text_surf.get_width() - 10,
        10,
        text_surf.get_width(),
        text_surf.get_height()
    )
    pg.draw.rect(screen, (0, 0, 0), timer_rect)

    #draw
    draw_bodies(bodies)
    screen.blit(text_surf, (screen_width - text_surf.get_width() - 10, 10))
    pg.display.flip()
    clock.tick(FPS)
