import pygame
import irsdk
import time

# Initialize Pygame
pygame.init()

# Set up the display with NOFRAME flag for a borderless window
screen = pygame.display.set_mode((800, 600), pygame.NOFRAME)
pygame.display.set_caption("iRacing Overlay")

# Define the draggable box area (e.g., top 40 pixels)
draggable_box = pygame.Rect(0, 0, 800, 40)
dragging = False
offset_x = 0
offset_y = 0

# Initialize iRacing SDK
ir = irsdk.IRSDK()
if not ir.startup():
    print("iRacing not running.")
    exit()

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if draggable_box.collidepoint(event.pos):
                    dragging = True
                    offset_x = draggable_box.x - event.pos[0]
                    offset_y = draggable_box.y - event.pos[1]
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                draggable_box.x = event.pos[0] + offset_x
                draggable_box.y = event.pos[1] + offset_y

    # Clear the screen
    screen.fill((0, 0, 0))

    # Fetch the latest data
    ir.freeze_var_buffer_latest()
    session_time = ir['SessionTime']
    speed_mps = ir['Speed']

    # Convert speed from meters per second to mph
    speed_mph = speed_mps * 2.23694

    # Determine color based on speed
    if speed_mph < 90:
        color = (255, 0, 0)  # Red
    elif 90 <= speed_mph <= 120:
        color = (255, 255, 0)  # Yellow
    else:
        color = (0, 255, 0)  # Green

    # Render the data
    font = pygame.font.Font(None, 36)
    text = font.render("Time: {:.2f} Speed: {:.2f} mph".format(session_time, speed_mph), True, color)
    screen.blit(text, (draggable_box.x + 20, draggable_box.y + 20))

    # Draw the draggable box (optional, for visualization)
    pygame.draw.rect(screen, (255, 255, 255), draggable_box, 2)

    # Update the display
    pygame.display.flip()

    # Add a delay to match the iRacing update rate
    time.sleep(0.1)  # Adjust as needed (0.1 seconds = 100 milliseconds)

# Clean up
pygame.quit()
