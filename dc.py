import libtcodpy as tcod

SCREEN_WIDTH=80
SCREEN_HEIGHT=50
LIMIT_FPS=20
fullscreen = False

def initialize_game():
    font_path = 'arial10x10.png'
    font_flags = tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD
    tcod.console_set_custom_font(font_path, font_flags)
    window_title = 'Dungeon Chef - a Saul Special'
    tcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, window_title, fullscreen)
    global con 
    con = tcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

    tcod.sys_set_fps(LIMIT_FPS)

    global player_x, player_y
    player_x = int(SCREEN_WIDTH/2)
    player_y = int(SCREEN_HEIGHT/2)

def handle_keys():
    global player_x, player_y

    # REAL TIME PLAY
    key = tcod.console_check_for_keypress()

    if key.vk == tcod.KEY_ENTER and key.lalt:
        tcod.console_set_fullscreen(not tcod.console_is_fullscreen())
    elif key.vk == tcod.KEY_ESCAPE:
        return True


    if tcod.console_is_key_pressed(tcod.KEY_UP):
        player_y -= 1
    elif tcod.console_is_key_pressed(tcod.KEY_DOWN):
        player_y += 1
    elif tcod.console_is_key_pressed(tcod.KEY_LEFT):
        player_x -= 1
    elif tcod.console_is_key_pressed(tcod.KEY_RIGHT):
        player_x += 1
    

def main():
    global con
    initialize_game()

    exit_game = False
    while not tcod.console_is_window_closed() and not exit_game:
        tcod.console_set_default_foreground(con, tcod.white)
        tcod.console_put_char(con, player_x, player_y, '@', tcod.BKGND_NONE)
        tcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
        tcod.console_flush()
        tcod.console_put_char(con, player_x, player_y, ' ', tcod.BKGND_NONE)
        exit_game = handle_keys()

main()
