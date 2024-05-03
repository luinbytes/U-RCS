import pygame
import math
from pygame.locals import *

# Initialize pygame
pygame.init()

# Set up display
WINDOW_SIZE = (1920, 1080)
screen = pygame.display.set_mode(WINDOW_SIZE, flags=pygame.SRCALPHA)  # Use SRCALPHA flag for transparency
pygame.display.set_caption("RCS plotter tester B)")

# Colors
BLACK = (0, 0, 0, 255)  # Include alpha channel for transparency
WHITE = (255, 255, 255, 200)  # Set alpha channel to control transparency
RED = (255, 0, 0)

# Variables
points = []  # List to store recorded points
drawing = True  # Set drawing mode to True initially
invert = False  # Set invert mode to False initially

# Font
font = pygame.font.Font(None, 20)

# Function to draw Bezier curve
def draw_curve(points):
    if len(points) < 3:
        return

    # Calculate Bezier curve
    curve_points = []
    for t in range(101):
        t /= 100
        x = sum(bi * point[0] * (1 - t) ** (len(points) - 1 - i) * t ** i for i, bi, point in zip(range(len(points)), bernstein(len(points)), points))
        y = sum(bi * point[1] * (1 - t) ** (len(points) - 1 - i) * t ** i for i, bi, point in zip(range(len(points)), bernstein(len(points)), points))
        curve_points.append((int(x), int(y)))

    if invert:  # If invert mode is active
        anchor_x, anchor_y = points[0]  # Anchor point coordinates
        delta_x = points[-1][0] - anchor_x  # Horizontal distance from anchor point
        delta_y = points[-1][1] - anchor_y  # Vertical distance from anchor point
        curve_points = [(anchor_x - (x - anchor_x), anchor_y - (y - anchor_y)) for x, y in curve_points]  # Adjust horizontally and vertically

    pygame.draw.lines(screen, RED, False, curve_points, 2)
    pygame.draw.circle(screen, RED, points[0], 4)  # Start point
    pygame.draw.circle(screen, RED, points[-1], 4)  # End point

    # Display coefficients of the Bezier curve
    curve_coefficients_text = font.render(f"Curve Coefficients: {list(bernstein(len(points)))}", True, BLACK)
    screen.blit(curve_coefficients_text, (10, 50))

    # Display invert status
    invert_text = font.render("Invert: On" if invert else "Invert: Off", True, BLACK)
    screen.blit(invert_text, (10, 90))

# Function to calculate Bernstein polynomial coefficients
def bernstein(n):
    for i in range(n):
        yield math.comb(n-1, i)

# Main loop
running = True
while running:
    screen.fill((0, 0, 0, 0))

    # Draw semi-transparent background
    pygame.draw.rect(screen, WHITE, screen.get_rect(), 0)

    # Display mode information
    mode_text = font.render("Mode: Drawing" if drawing else "Mode: Ready", True, BLACK)
    screen.blit(mode_text, (10, 10))

    # Display mouse coordinates
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_pos_text = font.render(f"Mouse: ({mouse_x}, {mouse_y})", True, BLACK)
    screen.blit(mouse_pos_text, (10, 30))

    # Display current point index
    if drawing:
        current_point_text = font.render(f"Current Point Index: {len(points) + 1}", True, BLACK)
        screen.blit(current_point_text, (10, 70))

    # Display each plotted point location
    plotted_points_text = font.render("Plotted Points:", True, BLACK)
    screen.blit(plotted_points_text, (10, 110))
    for i, point in enumerate(points):
        point_text = font.render(f"Point {i + 1}: ({point[0]}, {point[1]})", True, BLACK)
        screen.blit(point_text, (20, 130 + i * 20))

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if drawing and len(points) < 100:
                    points.append(pygame.mouse.get_pos())
                elif not drawing:
                    # Reset points if not in drawing mode
                    points = []
                    drawing = True

        elif event.type == KEYDOWN:
            if event.key == K_SPACE:  # Draw curve when 'Space' key is pressed
                if len(points) >= 2:
                    draw_curve(points)
                    drawing = False
            elif event.key == K_i:  # Toggle invert mode when 'i' key is pressed
                invert = not invert

    # Draw points
    for point in points:
        pygame.draw.circle(screen, BLACK, point, 4)

    # Draw curve if all points have been plotted
    if not drawing:
        draw_curve(points)

    pygame.display.update()

pygame.quit()
