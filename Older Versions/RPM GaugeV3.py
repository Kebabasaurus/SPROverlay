import pygame
import irsdk
import math

# Initialize Pygame
pygame.init()

# Set up the display with NOFRAME flag for a borderless window
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
pygame.display.set_caption("iRacing Overlay")

# Define the draggable state
dragging = False
drag_start_x = 0
drag_start_y = 0

# Initialize iRacing SDK
ir = irsdk.IRSDK()
if not ir.startup():
    print("iRacing not running.")
    exit()

# Define RPM gauge parameters
gauge_center = (600, 300)
gauge_radius = 100

# Create a clock object to manage frame rate
clock = pygame.time.Clock()

def draw_rpm_gauge(surface, center, radius, rpm, max_rpm):
    # Draw the outer circle of the gauge
    pygame.draw.circle(surface, (255, 255, 255), center, radius, 2)
    
    # Draw the inner circle of the gauge
    pygame.draw.circle(surface, (0, 0, 0), center, radius - 10)

    # Draw RPM blobs
    num_blobs = 20
    angle_step = 360 / num_blobs
    
    for i in range(num_blobs):
        angle = math.radians(i * angle_step)
        blob_radius = 5 + (rpm / max_rpm) * 30  # Adjust size based on RPM
        blob_x = center[0] + (radius - 15) * math.cos(angle)
        blob_y = center[1] - (radius - 15) * math.sin(angle)
        
        # Determine color based on RPM thresholds
        if rpm < (max_rpm * 0.33):
            blob_color = (255, 0, 0)  # Red for low RPM (0-33%)
        elif rpm < (max_rpm * 0.66):
            blob_color = (255, 255, 0)  # Yellow for medium RPM (33-66%)
        elif rpm < (max_rpm * 0.95):
            blob_color = (0, 255, 0)  # Green for high RPM (66-95%)
        else:
            blob_color = (0, 255, 255)  # Cyan for very high RPM (95%+)
        
        pygame.draw.circle(surface, blob_color, (int(blob_x), int(blob_y)), int(blob_radius))

    # Render the RPM value at the bottom of the gauge
    font = pygame.font.Font(None, 24)
    rpm_text = font.render(f"{rpm:.0f} RPM", True, (255, 255, 255))
    text_rect = rpm_text.get_rect(center=(center[0], center[1] + radius + 30))  # Adjust positioning below the gauge
    surface.blit(rpm_text, text_rect)

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
                # Start dragging
                dragging = True
                drag_start_x, drag_start_y = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                # Stop dragging
                dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                # Move the window
                mouse_x, mouse_y = pygame.mouse.get_pos()
                x, y = pygame.display.get_surface().get_rect().topleft
                new_x = x + (mouse_x - drag_start_x)
                new_y = y + (mouse_y - drag_start_y)
                
                # Set the new window position
                screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
                pygame.display.get_surface().get_rect().topleft = (new_x, new_y)

                drag_start_x, drag_start_y = event.pos

    # Clear the screen
    screen.fill((0, 0, 0))

    # Fetch the latest data
    ir.freeze_var_buffer_latest()
    session_time = ir['SessionTime']
    speed_mps = ir['Speed']
    rpm = ir['RPM']
    gear = ir['Gear']  # Fetch the gear data

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
    screen.blit(text, (20, 20))

    # Draw the RPM gauge with blobs
    draw_rpm_gauge(screen, gauge_center, gauge_radius, rpm, 10000)  # Assuming 10000 RPM is the max RPM

    # Render the Gear in big text
    gear_font = pygame.font.Font(None, 72)
    gear_text = gear_font.render(f"Gear: {gear}", True, (255, 255, 255))
    gear_text_rect = gear_text.get_rect(center=(gauge_center[0], gauge_center[1] - gauge_radius - 60))  # Adjust positioning above the gauge
    screen.blit(gear_text, gear_text_rect)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate to 100 FPS
    clock.tick(100)  # 100 FPS

# Clean up
pygame.quit()
