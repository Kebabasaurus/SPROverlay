import pygame
import irsdk
import math
import win32gui
import win32con
import win32api

# Initialize Pygame
pygame.init()

# Initial window mode
borderless = True

def set_window_mode(borderless):
    """ Set window mode to borderless or normal. """
    global screen, screen_width, screen_height
    flags = pygame.NOFRAME if borderless else pygame.RESIZABLE
    screen = pygame.display.set_mode((screen_width, screen_height), flags)
    pygame.display.set_caption("iRacing Overlay")

    if borderless:
        # Make the window always on top (Windows only)
        hwnd = pygame.display.get_wm_info()['window']
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)

        # Set window style to WS_EX_LAYERED to enable transparency
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style | win32con.WS_EX_LAYERED)
        
        # Set the transparency (0 is fully transparent, 255 is fully opaque)
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 200, win32con.LWA_COLORKEY | win32con.LWA_ALPHA)

def draw_button(surface, rect, text):
    """ Draw a button on the screen. """
    pygame.draw.rect(surface, (0, 0, 255), rect)  # Blue background
    pygame.draw.rect(surface, (255, 255, 255), rect, 2)  # White border
    font = pygame.font.Font(None, 20)  # Smaller font size for the button text
    text_surf = font.render(text, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)

def is_point_in_rect(point, rect):
    """ Check if a point is inside a rectangle. """
    x, y = point
    return rect.left <= x <= rect.right and rect.top <= y <= rect.bottom

def draw_fuel_display(surface, center, radius, fuel_percentage):
    """ Draw the fuel display in the middle of the screen. """
    pygame.draw.circle(surface, (0, 0, 0), center, radius)  # Black background circle
    pygame.draw.circle(surface, (255, 255, 255), center, radius, 2)  # White border

    # Render the fuel percentage
    font = pygame.font.Font(None, 36)
    fuel_text = font.render(f"Fuel: {fuel_percentage:.1f}%", True, (255, 255, 255))
    text_rect = fuel_text.get_rect(center=center)
    surface.blit(fuel_text, text_rect)

def draw_gradient_circle(surface, center, radius):
    """ Draw a gradient circle from outside to inside with a blue color scheme. """
    for r in range(radius, 0, -1):
        alpha = int(255 * (r / radius))  # Fading effect
        color = (0, 0, 255, alpha)  # Blue with varying alpha
        pygame.draw.circle(surface, color, center, r)

def draw_rpm_gauge(surface, center, radius, rpm, max_rpm, gear):
    """ Draw the RPM gauge with blobs and gear number. """
    # Draw the outer circle of the gauge
    pygame.draw.circle(surface, (255, 255, 255), center, radius, 2)
    
    # Draw the inner circle of the gauge
    pygame.draw.circle(surface, (0, 0, 0), center, radius - 10)

    # Draw RPM blobs
    num_blobs = 5000
    angle_step = 360 / num_blobs
    
    for i in range(num_blobs):
        angle = math.radians(i * angle_step)
        blob_radius = 5 + (rpm / max_rpm) * 30  # Adjust size based on RPM
        blob_x = center[0] + (radius - 15) * math.cos(angle)
        blob_y = center[1] - (radius - 15) * math.sin(angle)
        
        # Determine color based on RPM thresholds
        if rpm is not None:
            if rpm < (max_rpm * 0.33):
                blob_color = (255, 0, 0)  # Red for low RPM (0-33%)
            elif rpm < (max_rpm * 0.66):
                blob_color = (255, 255, 0)  # Yellow for medium RPM (33-66%)
            elif rpm < (max_rpm * 0.95):
                blob_color = (0, 255, 0)  # Green for high RPM (66-95%)
            else:
                blob_color = (0, 255, 255)  # Cyan for very high RPM (95%+)
        else:
            blob_color = (255, 255, 255)  # Default to white if RPM is None
        
        pygame.draw.circle(surface, blob_color, (int(blob_x), int(blob_y)), int(blob_radius))

    # Draw gradient circle behind the gear number
    draw_gradient_circle(surface, center, int(radius * 0.6))  # Adjust size for visibility

    # Render the RPM value at the bottom of the gauge
    font = pygame.font.Font(None, 24)
    rpm_text = font.render(f"{rpm:.0f} RPM" if rpm is not None else "RPM: N/A", True, (255, 255, 255))
    text_rect = rpm_text.get_rect(center=(center[0], center[1] + radius + 30))  # Adjust positioning below the gauge
    surface.blit(rpm_text, text_rect)

    # Render the Gear number inside the gauge with gradient circle background
    gear_font_size = int(radius * gear_font_ratio)  # Increased font size
    gear_font = pygame.font.Font(None, gear_font_size)  # Font size adjusted
    gear_text = gear_font.render(f"{gear}" if gear is not None else "Gear: N/A", True, (255, 255, 255))
    gear_text_rect = gear_text.get_rect(center=center)  # Centered inside the gauge
    surface.blit(gear_text, gear_text_rect)

def draw_bar(surface, x, y, width, height, percentage, color):
    """ Draw a bar with a specified percentage and color. """
    # Draw the background of the bar
    pygame.draw.rect(surface, (50, 50, 50), (x, y, width, height))
    pygame.draw.rect(surface, (255, 255, 255), (x, y, width, height), 2)  # Border
    
    # Draw the fill based on percentage
    fill_height = (percentage / 100) * height
    pygame.draw.rect(surface, color, (x, y + height - fill_height, width, fill_height))

    # Render the percentage text
    font = pygame.font.Font(None, 24)
    percentage_text = font.render(f"{percentage:.0f}%" if percentage is not None else "0%", True, (255, 255, 255))
    text_rect = percentage_text.get_rect(center=(x + width / 2, y + height / 2))
    surface.blit(percentage_text, text_rect)

# Set up the display with NOFRAME flag for a borderless window initially
screen_width, screen_height = 500, 250
set_window_mode(borderless)  # Initialize with borderless mode

# Initialize iRacing SDK
ir = irsdk.IRSDK()
if not ir.startup():
    print("iRacing not running.")
    exit()

# Define parameters for items (proportional to window size)
gauge_radius_ratio = 0.15
bar_width_ratio = 0.07
bar_height_ratio = 0.67
gear_font_ratio = 0.5  # Increased to make the gear number larger
fuel_radius_ratio = 0.1  # Ratio for the fuel display circle

# Create a clock object to manage frame rate
clock = pygame.time.Clock()

# Define dragging state
dragging_item = None
drag_start_x = 0
drag_start_y = 0
drag_sensitivity = 2  # Factor to increase dragging speed

# Define button rectangle for toggling window mode
button_width, button_height = 50, 30  # Smaller button size
button_rect = pygame.Rect((screen_width - button_width) // 2, screen_height - button_height - 10, button_width, button_height)

# Main loop
running = True
while running:
    # Update item dimensions and positions based on window size
    screen_width, screen_height = pygame.display.get_surface().get_size()
    
    # Adjust the vertical position to move the bars down
    vertical_offset = int(screen_height * 0.1)  # Increase this value to move the bars further down

    # Define item dimensions as proportions of the window size
    gauge_radius = int(screen_width * gauge_radius_ratio)
    throttle_bar_width = int(screen_width * bar_width_ratio)
    throttle_bar_height = int(screen_height * bar_height_ratio)
    brake_bar_width = throttle_bar_width
    brake_bar_height = throttle_bar_height
    gear_font_size = int(gauge_radius * gear_font_ratio)  # Font size based on gauge radius
    fuel_radius = int(screen_width * fuel_radius_ratio)  # Radius for the fuel display

    throttle_bar_x = int(screen_width * 0.02)
    throttle_bar_y = (screen_height - throttle_bar_height) // 2 + vertical_offset
    brake_bar_x = throttle_bar_x + throttle_bar_width + int(screen_width * 0.02)
    brake_bar_y = throttle_bar_y

    gauge_center = [int(screen_width * 0.75), int(screen_height * 0.5)]
    fuel_center = [int(screen_width * 0.5) - 50, int(screen_height * 0.5)]  # Move the fuel display 50 pixels to the left

    # Create invisible rectangles for draggable items
    gauge_rect = pygame.Rect(gauge_center[0] - gauge_radius, gauge_center[1] - gauge_radius, gauge_radius * 2, gauge_radius * 2)
    throttle_rect = pygame.Rect(throttle_bar_x, throttle_bar_y, throttle_bar_width, throttle_bar_height)
    brake_rect = pygame.Rect(brake_bar_x, brake_bar_y, brake_bar_width, brake_bar_height)
    fuel_rect = pygame.Rect(fuel_center[0] - fuel_radius, fuel_center[1] - fuel_radius, fuel_radius * 2, fuel_radius * 2)

    dragging_item = None  # Reset dragging state
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if is_point_in_rect(event.pos, gauge_rect):
                    dragging_item = 'gauge'
                elif is_point_in_rect(event.pos, throttle_rect):
                    dragging_item = 'throttle'
                elif is_point_in_rect(event.pos, brake_rect):
                    dragging_item = 'brake'
                elif is_point_in_rect(event.pos, fuel_rect):
                    dragging_item = 'fuel'
                elif is_point_in_rect(event.pos, button_rect):
                    # Toggle borderless mode on button click
                    borderless = not borderless
                    set_window_mode(borderless)
                if dragging_item:
                    drag_start_x, drag_start_y = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                dragging_item = None
        elif event.type == pygame.MOUSEMOTION:
            if dragging_item:
                mouse_x, mouse_y = event.pos
                dx = (mouse_x - drag_start_x) * drag_sensitivity  # Scale the dragging speed
                dy = (mouse_y - drag_start_y) * drag_sensitivity  # Scale the dragging speed
                
                if dragging_item == 'gauge':
                    gauge_center[0] += dx
                    gauge_center[1] += dy
                    gauge_rect.topleft = (gauge_center[0] - gauge_radius, gauge_center[1] - gauge_radius)
                elif dragging_item == 'throttle':
                    throttle_bar_x += dx
                    throttle_bar_y += dy
                    throttle_rect.topleft = (throttle_bar_x, throttle_bar_y)
                elif dragging_item == 'brake':
                    brake_bar_x += dx
                    brake_bar_y += dy
                    brake_rect.topleft = (brake_bar_x, brake_bar_y)
                elif dragging_item == 'fuel':
                    fuel_center[0] += dx
                    fuel_center[1] += dy
                    fuel_rect.topleft = (fuel_center[0] - fuel_radius, fuel_center[1] - fuel_radius)
                
                drag_start_x, drag_start_y = event.pos

    # Clear the screen with a transparent color
    screen.fill((0, 0, 0, 0))  # RGBA with 0 alpha for transparency

    # Fetch the latest data
    ir.freeze_var_buffer_latest()
    session_time = ir['SessionTime']
    speed_mps = ir['Speed']
    rpm = ir['RPM']
    gear = ir['Gear']  # Fetch the gear data
    throttle_percentage = ir['Throttle'] * 100
    brake_percentage = ir['Brake'] * 100
    lap_time = ir['LastLapTime']  # Fetch the current lap time
    fuel_percentage = ir['FuelLevel'] * 100  # Fetch the fuel percentage data

    # Handle None values
    if lap_time is None:
        lap_time = 0.0
    if speed_mps is None:
        speed_mps = 0.0
    if rpm is None:
        rpm = 0.0
    if gear is None:
        gear = "N/A"
    if throttle_percentage is None:
        throttle_percentage = 0.0
    if brake_percentage is None:
        brake_percentage = 0.0
    if fuel_percentage is None:
        fuel_percentage = 0.0

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
    text = font.render(f"Lap Time: {lap_time:.2f} Speed: {speed_mph:.2f} mph", True, color)
    screen.blit(text, (20, 20))

    # Draw the RPM gauge with blobs
    draw_rpm_gauge(screen, gauge_center, gauge_radius, rpm, 10000, gear)  # Assuming 10000 RPM is the max RPM

    # Draw the throttle and brake bars
    draw_bar(screen, throttle_bar_x, throttle_bar_y, throttle_bar_width, throttle_bar_height, throttle_percentage, (0, 255, 0))
    draw_bar(screen, brake_bar_x, brake_bar_y, brake_bar_width, brake_bar_height, brake_percentage, (255, 0, 0))

    # Draw the fuel display
    draw_fuel_display(screen, fuel_center, fuel_radius, fuel_percentage)

    # Draw the button
    draw_button(screen, button_rect, "TB")

    # Update the display
    pygame.display.flip()

    # Cap the frame rate to 30 FPS
    clock.tick(30)  # 30 FPS

# Clean up
pygame.quit()
