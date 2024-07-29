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
needle_length = 80

# Define fuel gauge parameters
fuel_gauge_center = (200, 300)
fuel_gauge_radius = 100

# Create a clock object to manage frame rate
clock = pygame.time.Clock()

def draw_rpm_gauge(surface, center, radius, rpm, max_rpm):
    # Draw the outer circle of the gauge
    pygame.draw.circle(surface, (255, 255, 255), center, radius, 2)
    
    # Draw the inner circle of the gauge
    pygame.draw.circle(surface, (0, 0, 0), center, radius - 10)

    # Calculate the angle of the needle
    rpm_angle = (rpm / max_rpm) * 270 - 135  # Map RPM to angle (-135 to 135 degrees)
    rpm_angle_rad = math.radians(rpm_angle)

    # Calculate the needle position
    needle_end_x = center[0] + needle_length * math.cos(rpm_angle_rad)
    needle_end_y = center[1] - needle_length * math.sin(rpm_angle_rad)

    # Draw the needle
    pygame.draw.line(surface, (255, 0, 0), center, (needle_end_x, needle_end_y), 2)

    # Draw RPM ticks and labels
    font = pygame.font.Font(None, 24)
    for i in range(0, max_rpm + 1, int(max_rpm / 5)):
        angle = (i / max_rpm) * 270 - 135
        angle_rad = math.radians(angle)
        tick_length = radius - 15
        tick_end_x = center[0] + tick_length * math.cos(angle_rad)
        tick_end_y = center[1] - tick_length * math.sin(angle_rad)
        pygame.draw.line(surface, (255, 255, 255), (center[0] + (radius - 10) * math.cos(angle_rad), center[1] - (radius - 10) * math.sin(angle_rad)), (tick_end_x, tick_end_y), 2)
        text = font.render(str(i), True, (255, 255, 255))
        text_rect = text.get_rect(center=(tick_end_x, tick_end_y - 15))
        surface.blit(text, text_rect)
    
    # Render the RPM value at the bottom of the gauge
    rpm_text = font.render(f"{rpm:.0f} RPM", True, (255, 255, 255))
    text_rect = rpm_text.get_rect(center=(center[0], center[1] + radius + 30))  # Adjust positioning below the gauge
    surface.blit(rpm_text, text_rect)

def draw_fuel_gauge(surface, center, radius, fuel, total_fuel):
    if fuel is None or total_fuel is None:
        return
    
    # Draw the outer circle of the fuel gauge
    pygame.draw.circle(surface, (255, 255, 255), center, radius, 2)
    
    # Draw the inner circle of the fuel gauge
    pygame.draw.circle(surface, (0, 0, 0), center, radius - 10)
    
    # Draw the fuel level as a filled arc
    fuel_percentage = fuel / total_fuel if total_fuel else 0
    start_angle = -90  # Starting angle (top of the circle)
    end_angle = start_angle + (fuel_percentage * 360)  # Calculate end angle based on fuel percentage
    
    pygame.draw.arc(surface, (0, 255, 0), pygame.Rect(center[0] - radius, center[1] - radius, 2 * radius, 2 * radius), 
                    math.radians(start_angle), math.radians(end_angle), 2)

    # Render the fuel value text in the center of the gauge
    font = pygame.font.Font(None, 24)
    fuel_text = font.render(f"{fuel:.1f}L/{total_fuel:.1f}L", True, (255, 255, 255))
    text_rect = fuel_text.get_rect(center=center)
    surface.blit(fuel_text, text_rect)

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
                pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
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
    fuel = ir['FuelLevel']  # Fuel remaining in liters
    total_fuel = ir['FuelCapacity']  # Total fuel capacity in liters

    # Print debug information
    print(f"Fuel: {fuel}, Total Fuel: {total_fuel}, Speed: {speed_mps}, RPM: {rpm}, Gear: {gear}")

    # Handle possible None values
    if speed_mps is None or rpm is None or fuel is None or total_fuel is None:
        continue  # Skip the frame if essential data is missing

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

    # Draw the RPM gauge
    draw_rpm_gauge(screen, gauge_center, gauge_radius, rpm, 10000)  # Assuming 10000 RPM is the max RPM

    # Draw the Fuel gauge
    draw_fuel_gauge(screen, fuel_gauge_center, fuel_gauge_radius, fuel, total_fuel)

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
