import pygame
import irsdk
import win32gui
import win32con
import win32api

# Settings Area
background = (0, 0, 0, 255)
window_x, window_y = 740, 830  # Window position

# Initialize Pygame
pygame.init()

# Initial window mode
borderless = True

def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = seconds % 60
    return f"{minutes:02}:{seconds:05.2f}"

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

# Set up the display with NOFRAME flag for a borderless window initially
screen_width, screen_height = 500, 250
screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
pygame.display.set_caption("iRacing Overlay")

# Move the window to a specific location
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
    screen.fill(background)

    # Fetch the latest data
    try:
        ir.freeze_var_buffer_latest()
        lap_delta_to_best_lap = ir['LapDeltaToBestLap']
    except KeyError as e:
        print(f"Key error: {e}")
        lap_delta_to_best_lap = 0.0

    # Handle None values
    lap_delta_to_best_lap = lap_delta_to_best_lap if lap_delta_to_best_lap is not None else 0.0

    # Render the data
    font = pygame.font.Font(None, 36)
    lap_delta_text = font.render(f"Delta to Best Lap: {format_time(lap_delta_to_best_lap)}", True, (174, 255, 0))
    screen.blit(lap_delta_text, (20, 20))

    # Draw the button
    draw_button(screen, button_rect, "TB")

    # Update the display
    pygame.display.flip()

    # Cap the frame rate to 20 FPS
    clock.tick(20)

pygame.quit()
