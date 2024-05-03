import pygame
import math
from pygame.locals import *
from datetime import datetime

# Initialize pygame
pygame.init()

# Set up display
WINDOW_SIZE = (1920, 1080)
screen = pygame.display.set_mode((WINDOW_SIZE), pygame.FULLSCREEN)  # Use SRCALPHA flag for transparency
pygame.display.set_caption("RCS plotter tester B)")

# Colors
DARK_GREY = (30, 30, 30)
PASTEL_PINK = (255, 192, 203)
CYAN = (0, 255, 255)
RED = (255, 0, 0)

# Variables
points = []  # List to store recorded points
drawing = True  # Set drawing mode to True initially
invert = False  # Set invert mode to False initially
window_size_toggle = False  # Set window size toggle to False initially

# Font
font = pygame.font.Font(None, 20)

# List to store inverted curve coordinates
inverted_curve_points = []

# Function to calculate Bernstein polynomial coefficients
def bernstein(n):
    for i in range(n):
        yield math.comb(n-1, i)

# Function to draw Bezier curve
def draw_curve(points):
    global inverted_curve_points
    if len(points) < 2:
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
        inverted_curve_points = [(anchor_x - (x - anchor_x), anchor_y - (y - anchor_y)) for x, y in curve_points]  # Adjust horizontally and vertically
        curve_points = inverted_curve_points

    pygame.draw.lines(screen, CYAN, False, curve_points, 2)
    pygame.draw.circle(screen, RED, points[0], 4)  # Start point
    pygame.draw.circle(screen, RED, points[-1], 4)  # End point

    # Display coefficients of the Bezier curve
    curve_coefficients_text = font.render(f"Curve Coefficients: {list(bernstein(len(points)))}", True, RED)
    screen.blit(curve_coefficients_text, (10, 70))

    # Display invert status
    invert_text = font.render("Invert: On" if invert else "Invert: Off", True, RED)
    screen.blit(invert_text, (10, 90))

# Main loop
running = True
while running:
    screen.fill(DARK_GREY)

    # Display mode information
    mode_text = font.render("Mode: Drawing" if drawing else "Mode: Ready", True, RED)
    screen.blit(mode_text, (10, 10))

    # Display fullscreen mode information
    fullscreen_text = font.render("Fullscreen: On" if screen.get_flags() & pygame.FULLSCREEN else "Fullscreen: Off", True, RED)
    screen.blit(fullscreen_text, (10, 30))

    # Display mouse coordinates
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_pos_text = font.render(f"Mouse: ({mouse_x}, {mouse_y})", True, RED)
    screen.blit(mouse_pos_text, (10, 50))

    # Display current point index
    if drawing:
        current_point_text = font.render(f"Current Point Index: {len(points) + 1}", True, RED)
        screen.blit(current_point_text, (10, 90))

    # Display each plotted point location
    plotted_points_text = font.render("Plotted Points:", True, RED)
    screen.blit(plotted_points_text, (10, 130))
    for i, point in enumerate(points):
        point_text = font.render(f"Point {i + 1}: ({point[0]}, {point[1]})", True, PASTEL_PINK)
        screen.blit(point_text, (20, 150 + i * 20))

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
            elif event.key == K_f:  # Toggle window size between 1920x1080 and 800x600 when 'f' key is pressed
                window_size_toggle = not window_size_toggle
                if window_size_toggle:
                    WINDOW_SIZE = (800, 600)
                    screen = pygame.display.set_mode(WINDOW_SIZE, flags=pygame.SRCALPHA)
                else:
                    WINDOW_SIZE = (1920, 1080)
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    # Draw points
    for point in points:
        pygame.draw.circle(screen, PASTEL_PINK, point, 4)

    # Draw curve if all points have been plotted
    if not drawing and len(points) >= 2:  # Check if there are at least 2 points
        draw_curve(points)

    pygame.display.update()

# Write inverted curve coordinates to a text file with current date and time as the name
if inverted_curve_points:
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"rcs_{current_datetime}.txt"
    with open(file_name, "w") as file:
        # Write REAL COORDS title
        file.write("[REAL COORDS]\n")
        for point in inverted_curve_points:
            file.write(f"{point[0]}, {point[1]}\n")

        # Write REBASED COORDS title
        file.write("\n[REBASED COORDS]\n")
        # Calculate the offset for rebase
        if inverted_curve_points:
            offset_x = inverted_curve_points[0][0]
            offset_y = inverted_curve_points[0][1]
        else:
            offset_x = 0
            offset_y = 0
        # Write rebased coordinates
        for point in inverted_curve_points:
            rebased_x = point[0] - offset_x
            rebased_y = point[1] - offset_y
            file.write(f"{rebased_x}, {rebased_y}\n")


pygame.quit()
