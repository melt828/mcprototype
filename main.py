import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from typing import List, Tuple, Optional
import math

# Initialize Pygame and OpenGL
pygame.init()
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
pygame.display.set_caption("Minecraft Prototype")

# Block types: (color, name)
BLOCK_TYPES = [
    ([0.0, 0.8, 0.0], "Grass"),
    ([0.5, 0.3, 0.0], "Dirt"),
    ([0.7, 0.7, 0.7], "Stone"),
    ([0.6, 0.4, 0.2], "Wood"),
]

def create_block(position, color):
    x, y, z = position
    vertices = [
        [x+0.5, y-0.5, z+0.5],    # Front-bottom-right
        [x+0.5, y+0.5, z+0.5],    # Front-top-right
        [x-0.5, y+0.5, z+0.5],    # Front-top-left
        [x-0.5, y-0.5, z+0.5],    # Front-bottom-left
        [x+0.5, y-0.5, z-0.5],    # Back-bottom-right
        [x+0.5, y+0.5, z-0.5],    # Back-top-right
        [x-0.5, y+0.5, z-0.5],    # Back-top-left
        [x-0.5, y-0.5, z-0.5],    # Back-bottom-left
    ]

    faces = [
        [0, 1, 2, 3],  # Front
        [4, 5, 1, 0],  # Right
        [7, 6, 5, 4],  # Back
        [3, 2, 6, 7],  # Left
        [1, 5, 6, 2],  # Top
        [4, 0, 3, 7],  # Bottom
    ]

    normals = [
        [0, 0, 1],   # Front
        [1, 0, 0],   # Right
        [0, 0, -1],  # Back
        [-1, 0, 0],  # Left
        [0, 1, 0],   # Top
        [0, -1, 0],  # Bottom
    ]

    glBegin(GL_QUADS)
    for i, face in enumerate(faces):
        glNormal3fv(normals[i])
        glColor3fv(color)
        for vertex in face:
            glVertex3fv(vertices[vertex])
    glEnd()

def get_targeted_block(blocks: List[Tuple], max_distance=5) -> Optional[Tuple]:
    """Return the first block hit by the player's view ray"""
    # Get player's look vector
    look_x = math.sin(math.radians(camera_rot[1]))
    look_y = -math.sin(math.radians(camera_rot[0])) * math.cos(math.radians(camera_rot[1]))
    look_z = -math.cos(math.radians(camera_rot[1])) * math.cos(math.radians(camera_rot[0]))
    
    # Check each block
    shortest_dist = float('inf')
    target_block = None
    
    for block in blocks:
        pos = block[0]
        # Vector from camera to block center
        dx = pos[0] - camera_pos[0]
        dy = pos[1] - camera_pos[1]
        dz = pos[2] - camera_pos[2]
        
        # Project onto look vector
        dist = (dx * look_x + dy * look_y + dz * look_z)
        
        if 0 < dist < max_distance:  # Block is in front and within range
            # Check if we're actually looking at it
            proj_x = camera_pos[0] + look_x * dist
            proj_y = camera_pos[1] + look_y * dist
            proj_z = camera_pos[2] + look_z * dist
            
            # Check if projection point is within block bounds
            if (abs(proj_x - pos[0]) < 0.5 and
                abs(proj_y - pos[1]) < 0.5 and
                abs(proj_z - pos[2]) < 0.5 and
                dist < shortest_dist):
                shortest_dist = dist
                target_block = block
    
    return target_block

def create_world():
    blocks = []
    # Create a cross pattern on the ground
    for x in range(-5, 6):
        # Create a line along X axis
        blocks.append(([x, -1, 0], BLOCK_TYPES[0][0]))  # Grass
        # Create a line along Z axis
        blocks.append(([0, -1, x], BLOCK_TYPES[1][0]))  # Dirt
    
    # Add a pillar in the center
    for y in range(-1, 3):
        blocks.append(([0, y, 0], BLOCK_TYPES[2][0]))  # Stone pillar
    
    print(f"Created {len(blocks)} blocks at ground level")
    return blocks

def move_camera():
    speed = 0.1
    keys = pygame.key.get_pressed()
    
    # Forward/Backward
    if keys[K_w]:
        camera_pos[2] -= speed * np.cos(np.radians(camera_rot[1]))
        camera_pos[0] += speed * np.sin(np.radians(camera_rot[1]))
    if keys[K_s]:
        camera_pos[2] += speed * np.cos(np.radians(camera_rot[1]))
        camera_pos[0] -= speed * np.sin(np.radians(camera_rot[1]))
    
    # Left/Right
    if keys[K_a]:
        camera_pos[0] -= speed * np.cos(np.radians(camera_rot[1]))
        camera_pos[2] -= speed * np.sin(np.radians(camera_rot[1]))
    if keys[K_d]:
        camera_pos[0] += speed * np.cos(np.radians(camera_rot[1]))
        camera_pos[2] += speed * np.sin(np.radians(camera_rot[1]))
    
    # Up/Down
    if keys[K_SPACE]:
        camera_pos[1] += speed
    if keys[K_LSHIFT]:
        camera_pos[1] -= speed

def handle_mouse():
    sensitivity = 0.5
    if pygame.mouse.get_visible():
        return
    
    mouse_rel = pygame.mouse.get_rel()
    camera_rot[1] += mouse_rel[0] * sensitivity  # Yaw
    camera_rot[0] -= mouse_rel[1] * sensitivity  # Pitch
    
    # Limit pitch to avoid over-rotation
    camera_rot[0] = max(-90, min(90, camera_rot[0]))

def draw_crosshair():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, display[0], display[1], 0, -1, 1)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Disable lighting for the crosshair
    glDisable(GL_LIGHTING)
    
    # Draw white crosshair
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_LINES)
    # Horizontal line
    glVertex2f(display[0]/2 - 10, display[1]/2)
    glVertex2f(display[0]/2 + 10, display[1]/2)
    # Vertical line
    glVertex2f(display[0]/2, display[1]/2 - 10)
    glVertex2f(display[0]/2, display[1]/2 + 10)
    glEnd()
    
    # Re-enable lighting
    glEnable(GL_LIGHTING)
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_block_outline(position):
    x, y, z = position
    vertices = [
        [x+0.5, y-0.5, z+0.5],    # Front-bottom-right
        [x+0.5, y+0.5, z+0.5],    # Front-top-right
        [x-0.5, y+0.5, z+0.5],    # Front-top-left
        [x-0.5, y-0.5, z+0.5],    # Front-bottom-left
        [x+0.5, y-0.5, z-0.5],    # Back-bottom-right
        [x+0.5, y+0.5, z-0.5],    # Back-top-right
        [x-0.5, y+0.5, z-0.5],    # Back-top-left
        [x-0.5, y-0.5, z-0.5],    # Back-bottom-left
    ]

    edges = [
        (0,1), (1,2), (2,3), (3,0),  # Front face
        (4,5), (5,6), (6,7), (7,4),  # Back face
        (0,4), (1,5), (2,6), (3,7)   # Connecting edges
    ]

    # Disable lighting for the outline
    glDisable(GL_LIGHTING)
    glColor3f(1.0, 1.0, 1.0)  # White outline
    glLineWidth(2.0)  # Thicker lines
    
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()
    
    # Reset line width and re-enable lighting
    glLineWidth(1.0)
    glEnable(GL_LIGHTING)

def main():
    # Set up the perspective
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)
    
    # Initial camera position and rotation
    global camera_pos, camera_rot
    camera_pos = [0.0, 2.0, 5.0]
    camera_rot = [30.0, 0.0]  # Look down slightly
    
    # Enable features
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    
    # Set up light
    glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 1.0, 0.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.6, 0.6, 0.6, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])

    blocks = create_world()
    print(f"Created {len(blocks)} blocks")  # Debug print
    
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    
    selected_block = 0
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.mouse.set_visible(True)
                    pygame.event.set_grab(False)
                elif event.key == K_q and pygame.mouse.get_visible():
                    pygame.quit()
                    return
                elif event.key == K_p:  # Print debug info
                    print(f"Camera position: {camera_pos}")
                    print(f"Camera rotation: {camera_rot}")
                    print(f"Number of blocks: {len(blocks)}")
                    print(f"First block position: {blocks[0][0] if blocks else 'No blocks'}")
                elif event.key == K_r:  # Reset camera
                    camera_pos[0] = 0.0
                    camera_pos[1] = 2.0
                    camera_pos[2] = 5.0
                    camera_rot[0] = 30.0
                    camera_rot[1] = 0.0
            elif event.type == pygame.MOUSEBUTTONDOWN and not pygame.mouse.get_visible():
                target = get_targeted_block(blocks)
                if target:
                    if event.button == 1:  # Left click - remove block
                        blocks.remove(target)
                    elif event.button == 3:  # Right click - place block
                        pos = target[0]
                        # Calculate placement position based on face hit
                        look_vec = [
                            math.sin(math.radians(camera_rot[1])),
                            -math.sin(math.radians(camera_rot[0])) * math.cos(math.radians(camera_rot[1])),
                            -math.cos(math.radians(camera_rot[1])) * math.cos(math.radians(camera_rot[0]))
                        ]
                        # Find which face was hit by checking largest component of look vector
                        max_comp = max(range(3), key=lambda i: abs(look_vec[i]))
                        new_pos = list(pos)
                        new_pos[max_comp] += -1 if look_vec[max_comp] > 0 else 1
                        blocks.append((new_pos, BLOCK_TYPES[selected_block][0]))
            elif event.type == pygame.MOUSEWHEEL:
                selected_block = (selected_block + event.y) % len(BLOCK_TYPES)
                print(f"Selected block: {BLOCK_TYPES[selected_block][1]}")

        move_camera()
        handle_mouse()

        # Clear the screen
        glClearColor(0.5, 0.7, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Set up camera view
        glLoadIdentity()
        glRotatef(camera_rot[0], 1, 0, 0)
        glRotatef(camera_rot[1], 0, 1, 0)
        glTranslatef(-camera_pos[0], -camera_pos[1], -camera_pos[2])

        # Draw all blocks
        for i, (position, color) in enumerate(blocks):
            create_block(position, color)
        
        # Draw outline of targeted block
        target = get_targeted_block(blocks)
        if target:
            draw_block_outline(target[0])
        
        draw_crosshair()
        
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main() 