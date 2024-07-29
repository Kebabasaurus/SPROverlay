import pygame
import irsdk
import time

# Initialize Pygame
pygame.init()

# Set up the display with NOFRAME flag for a borderless window
screen = pygame.display.set_mode((800, 600), pygame.NOFRAME)
pygame.display.set_caption("iRacing Overlay")

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

    # Clear the screen
    screen.fill((0, 0, 0))

    # Fetch the latest data
    ir.freeze_var_buffer_latest()
    session_time = ir['SessionTime']
    speed = ir['Speed']

    # Render the data
    font = pygame.font.Font(None, 36)
    text = font.render(f"Time: {session_time:.2f} Speed: {speed:.2f}", True, (255, 255, 255))
    screen.blit(text, (20, 20))

    # Update the display
    pygame.display.flip()

    # Add a delay to match the iRacing update rate
    pygame.time.wait(100)  # Adjust as needed

# Clean up
pygame.quit()
