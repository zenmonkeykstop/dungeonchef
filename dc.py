import libtcodpy as tcod

SCREEN_WIDTH=80
SCREEN_HEIGHT=50
LIMIT_FPS=20
fullscreen = False

MAP_WIDTH = 80
MAP_HEIGHT = 45

color_dark_wall = tcod.Color(172, 121, 101)
color_dark_ground = tcod.Color(193, 154, 165)

class Tile:
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked

        block_sight = blocked if block_sight is None else None
        self.block_sight = block_sight


class Object:
    # generic game objects
    def __init__(self, x, y, char, color):
        self.x = x
        self.y = y
        self.char = char
        self.color = color

    def move(self, dx, dy):
        if not map[self.x +dx][self.y +dy].blocked:
            self.x += dx
            self.y += dy
        else:
            self.x -= 3*dx
            self.y -= 3*dy

    def draw(self):
        tcod.console_set_default_foreground(con, self.color)
        tcod.console_put_char(con, self.x, self.y, self.char, tcod.BKGND_NONE)

    def clear(self):
        tcod.console_put_char(con, self.x, self.y, '.', tcod.BKGND_NONE)

def initialize_game():
    font_path = 'arial10x10.png'
    font_flags = tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD
    tcod.console_set_custom_font(font_path, font_flags)
    window_title = 'Dungeon Chef - a Saul Special'
    tcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, window_title, fullscreen)
    global con 
    con = tcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

    tcod.sys_set_fps(LIMIT_FPS)

def handle_keys():
    global player

    # REAL TIME PLAY
    key = tcod.console_check_for_keypress()

    if key.vk == tcod.KEY_ENTER and key.lalt:
        tcod.console_set_fullscreen(not tcod.console_is_fullscreen())
    elif key.vk == tcod.KEY_ESCAPE:
        return True


    if tcod.console_is_key_pressed(tcod.KEY_UP):
        player.move(0, -1)
    elif tcod.console_is_key_pressed(tcod.KEY_DOWN):
        player.move(0, 1)
    elif tcod.console_is_key_pressed(tcod.KEY_LEFT):
        player.move(-1, 0)
    elif tcod.console_is_key_pressed(tcod.KEY_RIGHT):
        player.move(1,0)

def make_map():
    global map

    map = [
            [Tile(False) for y in range(MAP_HEIGHT)]
            for x in range(MAP_WIDTH)
            ]

    map[30][22].blocked =True
    map[30][22].block_sight = True
    map[50][22].blocked = True
    map[50][22].block_sight = True

npc = Object(SCREEN_WIDTH //2 -5, SCREEN_HEIGHT //2, '@', tcod.yellow)
player = Object(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, '@', tcod.white)
objects = [npc, player]

def render_all():
    for object in objects:
        object.draw()

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            wall = map[x][y].block_sight
            if wall:
                tcod.console_set_char_background(con, x, y, color_dark_wall, 
                        tcod.BKGND_SET)
            else:
                tcod.console_set_char_background(con, x, y, color_dark_ground,
                        tcod.BKGND_SET)

    tcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)


def main():
    global con
    initialize_game()
    make_map()

    exit_game = False
    while not tcod.console_is_window_closed() and not exit_game:
        tcod.console_set_default_foreground(con, tcod.white)
        render_all()
        tcod.console_flush()
        for object in objects:
            object.clear()
        exit_game = handle_keys()

main()
