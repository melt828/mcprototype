import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# Initialize Pygame and OpenGL
pygame.init()
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
pygame.display.set_caption("3D Cube Test")

# Set up the perspective
gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
glTranslatef(0.0, 0.0, -5.0)

# Enable depth testing
glEnable(GL_DEPTH_TEST)

def draw_cube():
    vertices = [
        # Front face
        [-0.5, -0.5,  0.5],
        [ 0.5, -0.5,  0.5],
        [ 0.5,  0.5,  0.5],
        [-0.5,  0.5,  0.5],
        # Back face
        [-0.5, -0.5, -0.5],
        [ 0.5, -0.5, -0.5],
        [ 0.5,  0.5, -0.5],
        [-0.5,  0.5, -0.5],
        # Top face
        [-0.5,  0.5, -0.5],
        [ 0.5,  0.5, -0.5],
        [ 0.5,  0.5,  0.5],
        [-0.5,  0.5,  0.5],
        # Bottom face
        [-0.5, -0.5, -0.5],
        [ 0.5, -0.5, -0.5],
        [ 0.5, -0.5,  0.5],
        [-0.5, -0.5,  0.5],
        # Right face
        [ 0.5, -0.5, -0.5],
        [ 0.5,  0.5, -0.5],
        [ 0.5,  0.5,  0.5],
        [ 0.5, -0.5,  0.5],
        # Left face
        [-0.5, -0.5, -0.5],
        [-0.5,  0.5, -0.5],
        [-0.5,  0.5,  0.5],
        [-0.5, -0.5,  0.5]
    ]
    
    faces = [
        [0,1,2,3],  # Front
        [4,5,6,7],  # Back
        [8,9,10,11],  # Top
        [12,13,14,15],  # Bottom
        [16,17,18,19],  # Right
        [20,21,22,23]   # Left
    ]
    
    glBegin(GL_QUADS)
    for face in faces:
        for vertex in face:
            glVertex3fv(vertices[vertex])
    glEnd()

def main():
    rotation = 0
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    return

        # Clear the screen and depth buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.0, 0.0, 0.0, 1.0)  # Black background
        
        # Reset the view
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -5.0)
        glRotatef(rotation, 0, 1, 0)  # Rotate around Y axis
        glRotatef(rotation, 1, 0, 0)  # Rotate around X axis
        
        # Set color to red
        glColor3f(1.0, 0.0, 0.0)
        
        # Draw the cube
        draw_cube()
        
        # Update rotation
        rotation += 1
        
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main() 