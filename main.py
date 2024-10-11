import sys
from game import Game
from utilities import *

pygame.init()
opening_sound = pygame.mixer.Sound("resources/openingscreen.wav")
opening_sound.play()
programIcon = pygame.image.load('resources/gamepad_8141286.png')
pygame.display.set_icon(programIcon)
title_font = pygame.font.Font("resources/PressStart2P-Regular.ttf", 32)
standard_font = pygame.font.Font("resources/PressStart2P-Regular.ttf", 16)
instructions_font = pygame.font.Font("resources/PressStart2P-Regular.ttf", 10)
screen_width = 600
screen_height = 520
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()
title_surface = title_font.render("T E T R I S", True, Colors.neon_yellow)
title_message_surface = standard_font.render("Press any key to continue...", True, Colors.white)

# Starting Screen
start_screen = True
blink_timer = pygame.time.get_ticks()
blink_interval = 500
show_press_any_key = True
while start_screen:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            start_screen = False

    screen.fill(Colors.black)
    title_rect = title_surface.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
    press_any_key_rect = title_message_surface.get_rect(
        center=(screen_width // 2 + 15, screen_height // 2 + 50))
    screen.blit(title_surface, title_rect)

    current_time = pygame.time.get_ticks()
    if current_time - blink_timer >= blink_interval:
        show_press_any_key = not show_press_any_key
        blink_timer = current_time

    if show_press_any_key:
        screen.blit(title_message_surface, press_any_key_rect)

    pygame.display.update()
    clock.tick(60)

# Game Screen
user_game = Game()
GAME_UPDATE = pygame.USEREVENT
pygame.time.set_timer(GAME_UPDATE, 400)
pygame.mixer.music.load("resources/music.mp3")
pygame.mixer.music.play(-1)
hold_rect = pygame.Rect(30, 100, 130, 110)
score_rect = pygame.Rect(10, 300, 170, 60)
next_rect = pygame.Rect(455, 40, 130, 470)
game_over_rect = pygame.Rect(125, 250, 50, 50)
score_surface = standard_font.render("s c o r e", True, Colors.white)
hold_surface = standard_font.render("h o l d", True, Colors.white)
next_surface = standard_font.render("n e x t", True, Colors.white)
pause_surface = title_font.render("p a u s e", True, Colors.neon_yellow)
game_over_surface = title_font.render("G A M E  O V E R !", True, Colors.neon_yellow)
blink_timer = pygame.time.Clock()
blink_interval = 500
blink_visible = True

# Game Loop
game_restart = False
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if user_game.game_over:
                game_restart = True
                user_game.game_over = False
                user_game.reset()
            if not user_game.game_over and not user_game.pause and not game_restart:
                if event.key == pygame.K_LEFT:
                    user_game.move_left()
                if event.key == pygame.K_RIGHT:
                    user_game.move_right()
                if event.key == pygame.K_UP:
                    user_game.rotate()
                if event.key == pygame.K_DOWN:
                    user_game.soft_drop()
                if event.key == pygame.K_SPACE:
                    row_dropped_from = user_game.hard_drop()
                    user_game.update_score(0, row_dropped_from)
                if event.key == pygame.K_c:
                    user_game.hold_block()
            if event.key == pygame.K_ESCAPE and not user_game.game_over:
                user_game.pause = not user_game.pause
        if event.type == GAME_UPDATE and not user_game.game_over and not user_game.pause:
            user_game.soft_drop()
    if game_restart:
        game_restart = False

    # Draw the game
    screen.fill(Colors.black)
    if user_game.pause or user_game.game_over:
        pygame.draw.rect(screen, Colors.dark_gray, [0, 0, screen_width, screen_height])

    score_value_surface = standard_font.render(str(user_game.score), True, Colors.white)
    screen.blit(hold_surface, (40, 70, 50, 50))
    screen.blit(score_surface, (25, 270, 50, 50))
    screen.blit(next_surface, (470, 10, 50, 50))
    pygame.draw.rect(screen, Colors.darkest_gray, hold_rect, 0, 10)
    pygame.draw.rect(screen, Colors.darkest_gray, score_rect, 0, 10)
    pygame.draw.rect(screen, Colors.darkest_gray, next_rect, 0, 10)
    screen.blit(score_value_surface, score_value_surface.get_rect(centerx=score_rect.centerx, centery=score_rect.centery))
    user_game.draw(screen, paused=user_game.pause, game_over=user_game.game_over)

    if pygame.time.get_ticks() % (2 * blink_interval) < blink_interval:
        blink_visible = True
    else:
        blink_visible = False

    # Pause menu
    if user_game.pause:
        pygame.mixer.music.pause()
        pause_menu_surface = pygame.Surface((250, 200), pygame.SRCALPHA)
        pause_menu_surface.fill((0, 0, 0, 225))
        pause_surface_rect = pause_surface.get_rect(center=(screen_width // 2, 240))
        screen.blit(pause_surface, pause_surface_rect)
    else:
        pygame.mixer.music.unpause()

    if user_game.game_over:
        if blink_visible:
            game_over_surface_rect = game_over_surface.get_rect(center=(screen_width // 2, 240))
            screen.blit(game_over_surface, game_over_surface_rect)

    pygame.display.update()
    clock.tick(60)
