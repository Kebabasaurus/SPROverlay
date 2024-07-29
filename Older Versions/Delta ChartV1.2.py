import pygame
import irsdk
import math
import win32gui
import win32con
import win32api

# Settings Area------------------------------------------------------------------------------------------------------------
background = (0, 0, 0, 255)

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
        hwnd = pygame.display.get_wm_info()['window']
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)

        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 200, win32con.LWA_COLORKEY | win32con.LWA_ALPHA)

def move_window(x, y):
    """ Move the window to a specific position. """
    hwnd = pygame.display.get_wm_info()['window']
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, x, y, 0, 0, win32con.SWP_NOSIZE)

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

def draw_delta_bar(surface, rect, value):
    """ Draw a delta bar on the screen. """
    color = (0, 255, 0) if value < 0 else (255, 0, 0)  # Green for negative, Red for positive
    bar_width = min(abs(value) * 200, rect.width)  # Scale the width based on the value, max width is rect.width
    bar_rect = pygame.Rect(rect.x, rect.y, bar_width, rect.height)
    pygame.draw.rect(surface, color, bar_rect)

# Set up the display with NOFRAME flag for a borderless window initially
screen_width, screen_height = 500, 250
screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
pygame.display.set_caption("iRacing Overlay")

# Move the window to a specific location
window_x, window_y = 740, 830  # Set the desired coordinates here
move_window(window_x, window_y)

# Define button rectangle for toggling window mode
button_width, button_height = 50, 30
button_rect = pygame.Rect(screen_width - button_width - 10, 10, button_width, button_height)  # Position at top right

# Initialize iRacing SDK
ir = irsdk.IRSDK()
if not ir.startup():
    print("iRacing not running.")
    pygame.quit()
    exit()

# Create a clock object to manage frame rate
clock = pygame.time.Clock()

# Main loop
running = True
while running:
    screen_width, screen_height = pygame.display.get_surface().get_size()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if is_point_in_rect(event.pos, button_rect):
                    borderless = not borderless
                    set_window_mode(borderless)

    # Clear the screen with a transparent color
    screen.fill(background)  # No alpha needed here, just solid color for background 0,0,0 if you want clear.

    # Fetch the latest data
    try:
        ir.freeze_var_buffer_latest()
        lap_delta_to_best_lap = ir['LapDeltaToBestLap']
        lap_delta_to_session_last_lap = ir['LapDeltaToSessionLastlLap']
    except KeyError as e:
        print(f"Key error: {e}")
        lap_delta_to_best_lap = lap_delta_to_session_last_lap = 0.0

    # Render the data
    font = pygame.font.Font(None, 36)
    lap_delta_text = font.render(f"Lap Delta to Best Lap: {lap_delta_to_best_lap:.2f}", True, (174, 255, 0))  # Green for delta to best lap
    screen.blit(lap_delta_text, (20, 20))

    session_last_lap_text = font.render(f"Lap Delta to Last Lap: {lap_delta_to_session_last_lap:.2f}", True, (174, 255, 0))  # Green for delta to last lap
    screen.blit(session_last_lap_text, (20, 80))

    # Draw the delta bars
    draw_delta_bar(screen, pygame.Rect(20, 60, 200, 20), lap_delta_to_best_lap)
    draw_delta_bar(screen, pygame.Rect(20, 120, 200, 20), lap_delta_to_session_last_lap)

    # Draw the button
    draw_button(screen, button_rect, "TB")

    # Update the display
    pygame.display.flip()

    # Cap the frame rate to 20 FPS
    clock.tick(20)

pygame.quit()
