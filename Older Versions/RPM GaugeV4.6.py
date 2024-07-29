import pygame
import irsdk
import math
import win32gui
import win32con
import win32api

# Initialize Pygame
pygame.init()

# Set up the display with NOFRAME flag for a borderless window initially
screen_width, screen_height = 500, 250
screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
pygame.display.set_caption("iRacing Overlay")

# Function to set the window mode (borderless or normal)
def set_window_mode(borderless):
    global screen
    flags = pygame.NOFRAME if borderless else pygame.RESIZABLE
    screen = pygame.display.set_mode((screen_width, screen_height), flags)
    pygame.display.set_caption("iRacing Overlay")

    if borderless:
        hwnd = pygame.display.get_wm_info()['window']
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)

        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 200, win32con.LWA_COLORKEY | win32con.LWA_ALPHA)
    else:
        hwnd = pygame.display.get_wm_info()['window']
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style & ~(win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT))

# Function to move the window to a specific position
def move_window(x, y):
    hwnd = pygame.display.get_wm_info()['window']
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, x, y, 0, 0, win32con.SWP_NOSIZE)

# Drawing functions
def draw_button(surface, rect, text):
    pygame.draw.rect(surface, (0, 0, 255), rect)  # Blue background
    pygame.draw.rect(surface, (255, 255, 255), rect, 2)  # White border
    font = pygame.font.Font(None, 20)
    text_surf = font.render(text, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)

def is_point_in_rect(point, rect):
    x, y = point
    return rect.left <= x <= rect.right and rect.top <= y <= rect.bottom

def draw_fuel_display(surface, center, radius, fuel_percentage):
    pygame.draw.circle(surface, (0, 0, 0), center, radius)
    pygame.draw.circle(surface, (255, 255, 255), center, radius, 2)
    font = pygame.font.Font(None, 26)
    fuel_text = font.render(f"Fuel: {fuel_percentage:.1f}%", True, (255, 255, 255))
    text_rect = fuel_text.get_rect(center=center)
    surface.blit(fuel_text, text_rect)

def draw_gradient_circle(surface, center, radius):
    for r in range(radius, 0, -1):
        alpha = int(255 * (r / radius))
        color = (0, 0, 255, alpha)
        pygame.draw.circle(surface, color, center, r)

def draw_rpm_gauge(surface, center, radius, rpm, max_rpm, gear):
    pygame.draw.circle(surface, (255, 255, 255), center, radius, 2)
    pygame.draw.circle(surface, (0, 0, 0), center, radius - 10)
    num_blobs = 500
    angle_step = 360 / num_blobs
    for i in range(num_blobs):
        angle = math.radians(i * angle_step)
        blob_radius = 5 + (rpm / max_rpm) * 30
        blob_x = center[0] + (radius - 15) * math.cos(angle)
        blob_y = center[1] - (radius - 15) * math.sin(angle)
        
        if rpm < (max_rpm * 0.33):
            blob_color = (255, 0, 0)
        elif rpm < (max_rpm * 0.66):
            blob_color = (255, 255, 0)
        elif rpm < (max_rpm * 0.95):
            blob_color = (0, 255, 0)
        else:
            blob_color = (0, 255, 255)
        
        pygame.draw.circle(surface, blob_color, (int(blob_x), int(blob_y)), int(blob_radius))

    draw_gradient_circle(surface, center, int(radius * 0.6))
    font = pygame.font.Font(None, 24)
    rpm_text = font.render(f"{rpm:.0f} RPM" if rpm is not None else "RPM: N/A", True, (255, 255, 255))
    text_rect = rpm_text.get_rect(center=(center[0], center[1] + radius + 30))
    surface.blit(rpm_text, text_rect)

    gear_font_size = int(radius * gear_font_ratio)
    gear_font = pygame.font.Font(None, gear_font_size)
    gear_text = gear_font.render(f"{gear}" if gear is not None else "Gear: N/A", True, (255, 255, 255))
    gear_text_rect = gear_text.get_rect(center=center)
    surface.blit(gear_text, gear_text_rect)

def draw_bar(surface, x, y, width, height, percentage, color):
    pygame.draw.rect(surface, (50, 50, 50), (x, y, width, height))
    pygame.draw.rect(surface, (255, 255, 255), (x, y, width, height), 2)
    fill_height = (percentage / 100) * height
    pygame.draw.rect(surface, color, (x, y + height - fill_height, width, fill_height))
    font = pygame.font.Font(None, 24)
    percentage_text = font.render(f"{percentage:.0f}%" if percentage is not None else "0%", True, (255, 255, 255))
    text_rect = percentage_text.get_rect(center=(x + width / 2, y + height / 2))
    surface.blit(percentage_text, text_rect)

# Initialize iRacing SDK
ir = irsdk.IRSDK()
if not ir.startup():
    print("iRacing not running.")
    pygame.quit()
    exit()

# Parameters for items
gauge_radius_ratio = 0.15
bar_width_ratio = 0.07
bar_height_ratio = 0.67
gear_font_ratio = 0.5
fuel_radius_ratio = 0.1

# Clock object to manage frame rate
clock = pygame.time.Clock()

# Main loop
running = True
borderless = True
set_window_mode(borderless)

while running:
    # Update item dimensions and positions based on window size
    screen_width, screen_height = pygame.display.get_surface().get_size()
    vertical_offset = int(screen_height * 0.1)
    gauge_radius = int(screen_width * gauge_radius_ratio)
    throttle_bar_width = int(screen_width * bar_width_ratio)
    throttle_bar_height = int(screen_height * bar_height_ratio)
    brake_bar_width = throttle_bar_width
    brake_bar_height = throttle_bar_height
    gear_font_size = int(gauge_radius * gear_font_ratio)
    fuel_radius = int(screen_width * fuel_radius_ratio)

    throttle_bar_x = int(screen_width * 0.02)
    throttle_bar_y = (screen_height - throttle_bar_height) // 2 + vertical_offset
    brake_bar_x = throttle_bar_x + throttle_bar_width + int(screen_width * 0.02)
    brake_bar_y = throttle_bar_y
    gauge_center = [int(screen_width * 0.75), int(screen_height * 0.5)]
    fuel_center = [int(screen_width * 0.5) - 50, int(screen_height * 0.5)]

    # Create invisible rectangles for draggable items
    gauge_rect = pygame.Rect(gauge_center[0] - gauge_radius, gauge_center[1] - gauge_radius, gauge_radius * 2, gauge_radius * 2)
    throttle_rect = pygame.Rect(throttle_bar_x, throttle_bar_y, throttle_bar_width, throttle_bar_height)
    brake_rect = pygame.Rect(brake_bar_x, brake_bar_y, brake_bar_width, brake_bar_height)
    fuel_rect = pygame.Rect(fuel_center[0] - fuel_radius, fuel_center[1] - fuel_radius, fuel_radius * 2, fuel_radius * 2)
    button_rect = pygame.Rect(screen_width - button_width - 10, 10, button_width, button_height)

    dragging_item = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if is_point_in_rect(event.pos, gauge_rect):
                    dragging_item = 'gauge'
                elif is_point_in_rect(event.pos, throttle_rect):
                    dragging_item = 'throttle'
                elif is_point_in_rect(event.pos, brake_rect):
                    dragging_item = 'brake'
                elif is_point_in_rect(event.pos, fuel_rect):
                    dragging_item = 'fuel'
                elif is_point_in_rect(event.pos, button_rect):
                    borderless = not borderless
                    set_window_mode(borderless)
                if dragging_item:
                    drag_start_x, drag_start_y = event.pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            dragging_item = None
        elif event.type == pygame.MOUSEMOTION and dragging_item:
            mouse_x, mouse_y = event.pos
            dx = mouse_x - drag_start_x
            dy = mouse_y - drag_start_y
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

    # Clear the screen with a solid color
    screen.fill((0, 0, 0))

    # Fetch the latest data
    try:
        ir.freeze_var_buffer_latest()
        session_time = ir['SessionTime']
        speed_mps = ir['Speed']
        rpm = ir['RPM']
        gear = ir['Gear']
        throttle_percentage = ir['Throttle'] * 100
        brake_percentage = ir['Brake'] * 100
        lap_time = ir['LastLapTime']
        fuel_percentage = ir['FuelLevel'] * 100
    except KeyError as e:
        print(f"Key error: {e}")
        session_time = speed_mps = rpm = gear = 0.0
        throttle_percentage = brake_percentage = fuel_percentage = 0.0

    # Handle None values
    lap_time = lap_time if lap_time is not None else 0.0
    speed_mps = speed_mps if speed_mps is not None else 0.0
    rpm = rpm if rpm is not None else 0.0
    gear = gear if gear is not None else "N/A"
    throttle_percentage = throttle_percentage if throttle_percentage is not None else 0.0
    brake_percentage = brake_percentage if brake_percentage is not None else 0.0
    fuel_percentage = fuel_percentage if fuel_percentage is not None else 0.0

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
    draw_rpm_gauge(screen, gauge_center, gauge_radius, rpm, 10000, gear)

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
    clock.tick(30)

pygame.quit()
