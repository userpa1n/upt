import numpy as np
import pygame as pg
pg.init()
#figure out max speed and error and energy and stuff
#restart
#zoom to cursor
#presets and ui good and gui and ux and stuff
#camera on center of mass
#floating point in ui
#click planet to see info
#add planet(into orbit)


#constants, init

G = 6.6743e-11
dt = 86400 #seconds between frames
FPS = 360
bodies = []
SCALE = 1.4e10 #m/px
MIN_SCALE = 1.4e9
MAX_SCALE = 1.4e10
ZOOM_SPEED = 1/5
SPEED_CHANGE = 1.5

font = pg.font.SysFont("Arial", 20)
screen_width, screen_height = 720, 720
screen = pg.display.set_mode([screen_width, screen_height])
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
        self.trail = []
        self.maxtrailsize = 500 #too small for further planets
        bodies.append(self)


def calculate_force(body1, body2):
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
            body.acc += calculate_force(body, body2) / body.mass # a = f/m

def update(bodies, dt):
    for body in bodies:
        body.vel += body.acc*dt
        body.pos += body.vel*dt
        #save trail info
        body.trail.append(body.pos.copy())
        if len(body.trail) > body.maxtrailsize:
            body.trail.pop(0)

def world_to_screen(world_points): #[(x, y), (x, y)]
    screen_coords = []
    for world_point in world_points:
        screen_coords.append((world_point[0]/SCALE + screen_width//2, world_point[1]/SCALE + screen_height//2))
    return screen_coords

def screen_to_world(screen_points): #[(x, y), (x, y)]
    world_coords = []
    for screen_point in screen_points:
        world_coords.append(((screen_point[0]-screen_width//2)*SCALE, (screen_point[1]-screen_height//2)*SCALE))
    return world_coords

def draw_bodies(bodies):
    for body in bodies:
        pos = world_to_screen([body.pos])[0]
        r = 5
        pg.draw.circle(screen, body.color, pos, r)
        trail = world_to_screen(body.trail)
        if len(trail) > 2:
            pg.draw.lines(screen, body.color, False, trail, 1)
        name_surf = font.render(body.name, True, (255,255,255))
        screen.blit(name_surf, (pos[0]+8, pos[1]-8))

# Sun
sun = Body(
    mass=1.989e30,
    pos=np.array([0.0, 0.0]),
    vel=np.array([0.0, 0.0]),
    acc=np.zeros(2),
    name='Sun',
    color=(255, 255, 0),
)

# Mercury
mercury = Body(
    mass=3.3e23,
    pos=np.array([5.79e10, 0.0]),
    vel=np.array([0.0, 47_400]),
    acc=np.zeros(2),
    name='Mercury',
    color=(150, 150, 150),
)

# Venus
venus = Body(
    mass=4.87e24,
    pos=np.array([1.082e11, 0.0]),
    vel=np.array([0.0, 35_020]),
    acc=np.zeros(2),
    name='Venus',
    color=(255, 200, 150),
)

# Earth
earth = Body(
    mass=5.97e24,
    pos=np.array([1.496e11, 0.0]),
    vel=np.array([0.0, 29_780]),
    acc=np.zeros(2),
    name='Earth',
    color=(0, 150, 255),
)

# Mars
mars = Body(
    mass=6.42e23,
    pos=np.array([2.279e11, 0.0]),
    vel=np.array([0.0, 24_130]),
    acc=np.zeros(2),
    name='Mars',
    color=(255, 100, 50),
)

# Jupiter
jupiter = Body(
    mass=1.898e27,
    pos=np.array([7.785e11, 0.0]),
    vel=np.array([0.0, 13_070]),
    acc=np.zeros(2),
    name='Jupiter',
    color=(255, 150, 100),
)

# Saturn
saturn = Body(
    mass=5.683e26,
    pos=np.array([1.433e12, 0.0]),
    vel=np.array([0.0, 9_680]),
    acc=np.zeros(2),
    name='Saturn',
    color=(255, 220, 180),
)

# Uranus
uranus = Body(
    mass=8.681e25,
    pos=np.array([2.877e12, 0.0]),
    vel=np.array([0.0, 6_800]),
    acc=np.zeros(2),
    name='Uranus',
    color=(100, 200, 255),
)

# Neptune
neptune = Body(
    mass=1.024e26,
    pos=np.array([4.503e12, 0.0]),
    vel=np.array([0.0, 5_430]),
    acc=np.zeros(2),
    name='Neptune',
    color=(50, 100, 255),
)



#main pygame loop
clock = pg.time.Clock()
running = True
while running:
    #screen.blit(trails, (0, 0))
    screen.fill('black')
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
            #trails.fill('black') #clear trails
        #speed
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_LEFT:
                dt /= SPEED_CHANGE
            elif event.key == pg.K_RIGHT:
                dt *= SPEED_CHANGE
    #physics
    apply_acc(bodies)
    update(bodies, dt)

    #timer
    sim_time += dt
    days = int((sim_time // 86400 ) % 365)
    hours = int((sim_time % 86400) // 3600)
    minutes = int((sim_time % 3600) // 60)
    seconds = int(sim_time % 60)
    years = int(sim_time//86400//365)

    timer_text = f"{years}y {days}d {hours:02}h {minutes:02}m {seconds:02}s"
    speed_text = f'Speed: {dt} sec/frame'
    fps_text = f'FPS: {FPS}'


    timer_surf = font.render(timer_text, True, (255, 255, 255))
    speed_surf = font.render(speed_text, True, (255, 255, 255))
    fps_surf = font.render(fps_text, True, (255, 255, 255))


    #draw
    draw_bodies(bodies)
    hud = pg.Surface((300, 70))  
    hud.fill((0,0,0))             # black background
    hud.set_alpha(200)            # semi-transparent
    hud.blit(timer_surf, (0,0))
    hud.blit(speed_surf, (0,20))
    hud.blit(fps_surf, (0,40))
    screen.blit(hud, (0, 10))


    pg.display.flip()
    clock.tick(FPS)
