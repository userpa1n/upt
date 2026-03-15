import numpy as np
import pygame as pg
pg.init()
#figure out max speed and error and energy and stuff - should work now
#add softening back
#zoom to cursor
#ui good and gui and ux and stuff
#click planet to see info
#add planet(into orbit?)
#seperate popup screen for gui or smth idk man
#kaamera massikeskmes ei tööta


#CONTROLS
#SPACE - pause
#LEFT/RIGHT ARROW - slow/speed up (change dt)
#1, 2, 3 - load preset
#SCROLL - zoom


#constants, init
font = pg.font.SysFont("Arial", 20)
screen_width, screen_height = 720, 720
screen = pg.display.set_mode([screen_width, screen_height])


G = 6.6743e-11
dt = 60 #simulation seconds between frames, default value here
FPS = 360
bodies = []
ZOOM_SPEED = 1/6
SPEED_CHANGE = 1.5
sim_time = 0 #seconds
error = 0 #joules
starting_energy = 0
paused = False
#classes, functions
class Body:
    def __init__(self, mass, pos, vel, acc=0.0, name='', color='blue', maxtrailsize = 1000):
        self.mass = mass
        self.pos = np.array(pos, dtype=float)
        self.vel = np.array(vel, dtype=float)
        self.acc = np.array(acc, dtype=float)
        self.name = name
        self.color = color
        self.trail = []
        self.maxtrailsize = maxtrailsize
        bodies.append(self)


def calculate_force(body1, body2):
    softening = 1e4 #this is to avoid division by 0 and add stability when r is really small
    r_vec = body2.pos-body1.pos #vector from body1 to body2
    r = np.linalg.norm(r_vec) #vector length
    F_mag = G * body1.mass * body2.mass / (r**2+softening**2) #newtons law of gravity
    direction = r_vec/r #unit vector from body1 to body2
    F = F_mag*direction #force vector from body1 to body2
    return F

def apply_acc(bodies):
    for body in bodies:
        body.acc = np.zeros(2)
    for i in range(len(bodies)):
        body1 = bodies[i]
        for j in range(i+1, len(bodies)):
            body2 = bodies[j]
            force = calculate_force(body1, body2)
            body1.acc += force/body1.mass
            body2.acc += -force/body2.mass
    

def update(bodies, dt):
    old_accs = []
    for body in bodies:
        '''
    #semi-implicit euler: update velocity before position
        body.vel += body.acc*dt #v=at
        body.pos += body.vel*dt #s=vt
        apply_acc(bodies)
        '''
    #velocity verlet: find acc[i], update position, then find acc[i+1] and use acc = (acc[i]+acc[i+1])/2 to find velocity[i]
        body.pos += body.vel*dt + 0.5*body.acc*dt**2 # x += v0t + 0.5a*t**2
        old_accs.append(body.acc)

    apply_acc(bodies)
    counter = 0
    for body in bodies:
        body.vel += (old_accs[counter]+body.acc)/2 * dt
        counter += 1
    
    #save trail info
        if len(body.trail) == 0 or np.linalg.norm(body.pos - body.trail[-1]) > SCALE*2: #add new trail point only when planet has moved on screen
            body.trail.append(body.pos.copy())
            if len(body.trail) > body.maxtrailsize:
                body.trail.pop(0)

def kinetic_energy(body):
    return body.mass*np.linalg.norm(body.vel)**2 / 2

def potential_energy(body1, body2):
    softening = 1e4
    return -G*body1.mass*body2.mass / (np.linalg.norm(body2.pos-body1.pos)+softening)

def energy(bodies):
    kinetic = 0
    potential = 0
    for i in range(len(bodies)):
        body1 = bodies[i]
        kinetic += kinetic_energy(body1)
        for j in range(i+1, len(bodies)):
            body2 = bodies[j]
            potential += potential_energy(body1, body2)
    return kinetic + potential



def center_of_mass(bodies):
    if bodies:
        total_mass = sum(body.mass for body in bodies)
        weighted_mass_sum = sum(body.pos*body.mass for body in bodies)
        return weighted_mass_sum / total_mass

def world_to_screen(world_point, center): #(x, y)
    relative_pos = world_point-center
    screen_coord = (relative_pos[0]/SCALE + screen_width//2, relative_pos[1]/SCALE + screen_height//2)
    return screen_coord

def screen_to_world(screen_point): #(x, y)
    world_coord = ((screen_point[0]-screen_width//2)*SCALE, (screen_point[1]-screen_height//2)*SCALE)
    return world_coord

def draw_bodies(bodies):
    center = center_of_mass(bodies)
    for body in bodies:
        screen_pos = world_to_screen(body.pos, center)
        r = 5
        pg.draw.circle(screen, body.color, screen_pos, r)
        trail = [world_to_screen(point, center) for point in body.trail]
        if len(trail) > 2:
            pg.draw.lines(screen, body.color, False, trail, 1)
        name_surf = font.render(body.name, True, (255,255,255))
        screen.blit(name_surf, (screen_pos[0]+8, screen_pos[1]-8))

def clear_sim():
    global bodies, sim_time
    bodies.clear()
    sim_time = 0

def load_solar_system():
    global SCALE, MIN_SCALE, MAX_SCALE, dt, starting_energy
    SCALE = 1.4e10
    MIN_SCALE = 1e9
    MAX_SCALE = 1.4e10
    dt = 86400
    # Sun
    Body(
        mass=1.989e30,
        pos=np.array([0.0, 0.0]),
        vel=np.array([0.0, 0.0]),
        name='Sun',
        color=(255, 255, 0),
    )
    # Mercury
    Body(
        mass=3.3e23,
        pos=np.array([5.79e10, 0.0]),
        vel=np.array([0.0, 47_400]),
        name='Mercury',
        color=(150, 150, 150))
    # Venus
    Body(
        mass=4.87e24,
        pos=np.array([1.082e11, 0.0]),
        vel=np.array([0.0, 35_020]),
        acc=np.zeros(2),
        name='Venus',
        color=(255, 200, 150))
    # Earth
    Body(
        mass=5.97e24,
        pos=np.array([1.496e11, 0.0]),
        vel=np.array([0.0, 29_780]),
        name='Earth',
        color=(0, 150, 255))
    # Mars
    Body(
        mass=6.42e23,
        pos=np.array([2.279e11, 0.0]),
        vel=np.array([0.0, 24_130]),
        name='Mars',
        color=(255, 100, 50))
    # Jupiter
    Body(
        mass=1.898e27,
        pos=np.array([7.785e11, 0.0]),
        vel=np.array([0.0, 13_070]),
        name='Jupiter',
        color=(255, 150, 100))
    # Saturn
    Body(
        mass=5.683e26,
        pos=np.array([1.433e12, 0.0]),
        vel=np.array([0.0, 9_680]),
        name='Saturn',
        color=(255, 220, 180))
    # Uranus
    Body(
        mass=8.681e25,
        pos=np.array([2.877e12, 0.0]),
        vel=np.array([0.0, 6_800]),
        name='Uranus',
        color=(100, 200, 255))
    # Neptune
    Body(
        mass=1.024e26,
        pos=np.array([4.503e12, 0.0]),
        vel=np.array([0.0, 5_430]),
        name='Neptune',
        color=(50, 100, 255),
        maxtrailsize=2500)
    starting_energy = energy(bodies)
def load_figure_8():
    global SCALE, MIN_SCALE, MAX_SCALE, dt, starting_energy
    dt = 300
    SCALE = 1e8
    MIN_SCALE = 7e7
    MAX_SCALE = 5e8
    pos1 = (0.97000436, -0.24308753)
    vel1 = (0.46620368, 0.43236573)
    M = 1e30
    pos_scale = 2e10
    vel_scale = np.sqrt(G*M/pos_scale)
    Body(
        mass=M, 
        pos = np.array([pos1[0]*pos_scale, pos1[1]*pos_scale]), 
        vel = np.array([vel1[0]*vel_scale, vel1[1]*vel_scale]),
        name = '1',
        color=(0, 255, 255))
    Body(
        mass=M, 
        pos = np.array([0.0, 0.0]), 
        vel = np.array([-2 * vel1[0]*vel_scale, -2 * vel1[1]*vel_scale]),
        name = '2',
        color=(0, 255, 0))
    Body(
        mass=M, 
        pos = np.array([-pos1[0]*pos_scale, -pos1[1]*pos_scale]), 
        vel = np.array([vel1[0]*vel_scale, vel1[1]*vel_scale]),
        name = '3',
        color=(255, 0, 0))
    starting_energy = energy(bodies)
def load_triangle():
    global SCALE, MIN_SCALE, MAX_SCALE, dt, starting_energy
    dt = 300
    SCALE = 1e8
    MIN_SCALE = 6e7
    MAX_SCALE = 5e8
    v_mag = 13900 
    M = 1e30
    R = 2e10
    Body(
        mass=M,
        pos=np.array([R, 0.0]),
        vel=np.array([0.0, v_mag]),
        name='1', color=(255, 255, 0))
    Body(
        mass=M,
        pos=np.array([-R/2, R * np.sqrt(3)/2]),
        vel=np.array([-v_mag * np.sqrt(3)/2, -v_mag/2]),
        name='2', color=(255, 0, 255))
    Body(
        mass=M,
        pos=np.array([-R/2, -R * np.sqrt(3)/2]),
        vel=np.array([v_mag * np.sqrt(3)/2, -v_mag/2]),
        name='3', color=(0, 255, 255))
    starting_energy = energy(bodies)
load_solar_system()
starting_energy = energy(bodies)
#main pygame loop
clock = pg.time.Clock()
running = True
while running:
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
        
        elif event.type == pg.KEYDOWN:
            #speed
            if event.key == pg.K_LEFT:
                dt /= SPEED_CHANGE
            elif event.key == pg.K_RIGHT:
                dt *= SPEED_CHANGE
            elif event.key == pg.K_SPACE:
                paused = not paused
                
            #presets
            elif event.key == pg.K_1:
                clear_sim()
                load_solar_system()
            elif event.key == pg.K_2:
                clear_sim()
                load_triangle()
            elif event.key == pg.K_3:
                clear_sim()
                load_figure_8()
    
    if not paused:
        #physics
        update(bodies, dt)
        error = (energy(bodies)-starting_energy)/starting_energy*100
        sim_time += dt
    #timer
    
    days = int((sim_time // 86400 ) % 365)
    hours = int((sim_time % 86400) // 3600)
    minutes = int((sim_time % 3600) // 60)
    seconds = int(sim_time % 60)
    years = int(sim_time//86400//365)

    #text
    timer_text = f"{years}y {days}d {hours:02}h {minutes:02}m {seconds:02}s"
    speed_text = f'Speed: {round(dt, 4)} sec/frame'
    fps_text = f'MAX_FPS: {FPS}'
    tutorial_text = '1: solar system, 2: Lagrange triangle, 3:figure 8'
    energy_text = f'Energy error: {error:.1e}%'

    timer_surf = font.render(timer_text, True, (255, 255, 255))
    speed_surf = font.render(speed_text, True, (255, 255, 255))
    fps_surf = font.render(fps_text, True, (255, 255, 255))
    tutorial_surf = font.render(tutorial_text, True, (255, 255, 255))
    energy_surf = font.render(energy_text, True, (255, 255, 255))

    #draw hud
    draw_bodies(bodies)
    hud = pg.Surface((600, 120))  
    hud.fill((0,0,0))             # black background
    hud.set_alpha(100)            # semi-transparent
    hud.blit(timer_surf, (0,0))
    hud.blit(speed_surf, (0,20))
    hud.blit(fps_surf, (0,40))
    hud.blit(tutorial_surf, (0, 60))
    hud.blit(energy_surf, (0, 80))
    screen.blit(hud, (0, 10))


    pg.display.flip()
    clock.tick(FPS)
