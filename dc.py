# DUNGEON CHEF! Starting from the tutorial at:
# http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python3%2Blibtcod
#
# ABSOLUTELY DO NOT USE THIS AS CONTROL CODE FOR YOUR NUCLEAR POWER STATION
# NO WARRANTY OR GUARANTEES, NO REFUNDS, NO COMPLAINING

import libtcodpy as tcod
import math
import textwrap

SCREEN_WIDTH=80
SCREEN_HEIGHT=50
LIMIT_FPS=20
fullscreen = False

MAP_WIDTH = 80
MAP_HEIGHT = 43

color_dark_wall = tcod.Color(20,20,20)
color_light_wall = tcod.Color(182, 131, 111)
color_dark_ground = tcod.Color(40,40,40)
color_light_ground = tcod.Color(200, 180, 50)

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 60

FOV_ALGO = 0
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

MAX_ROOM_MONSTERS = 3

PLAYER_SPEED = 2
DEFAULT_SPEED = 10
DEFAULT_ATTACK_SPEED = 20

BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT

MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT -1

class Fighter:
    def __init__(self, hp, defense, power, death_function, 
            attack_speed=DEFAULT_ATTACK_SPEED):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        self.death_function = death_function
        self.attack_speed = attack_speed

    def take_damage(self, damage):
        if damage > 0:
            self.hp = max(0, self.hp - damage)
            if self.hp <= 0:
                function = self.death_function
                if function is not None:
                    function(self.owner)

    def attack(self, target):
        damage = self.power - target.fighter.defense

        if damage > 0:
            message(self.owner.name.capitalize() + 
                    ' attacks ' + target.name + ' for ' + str(damage) + 'hp!',
                    tcod.yellow)
            target.fighter.take_damage(damage)
        else:
            message(self.owner.name.capitalize() + 
                    ' attacks ' + target.name + ' but it does no damage...', 
                    tcod.green) 
        self.owner.wait = self.attack_speed

class BasicMonster:
    def take_turn(self):
        monster = self.owner
        if tcod.map_is_in_fov(fov_map, monster.x, monster.y):
            if monster.distance_to(player)>=2:
                monster.move_towards(player.x, player.y)
            elif player.fighter.hp > 0:
                monster.fighter.attack(player)



class Rect:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return (center_x, center_y)
 
    def intersect(self, other):
        #returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


class Tile:
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked
        self.explored = False
        block_sight = blocked if block_sight is None else None
        self.block_sight = block_sight


class Object:
    # generic game objects
    def __init__(self, x, y, char, color, name, 
            blocks=False, fighter = None, ai = None, speed=DEFAULT_SPEED):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks

        self.fighter = fighter
        if self.fighter:
            self.fighter.owner = self

        self.ai = ai
        if self.ai:
            self.ai.owner = self

        self.speed = speed
        self.wait = 0


    def send_to_back(self):
        global objects
        objects.remove(self)
        objects.insert(0, self)

    def move_towards(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt((dx ** 2) + (dy ** 2))
        dx = int(round(dx / distance))
        dy = int(round(dy /distance))
        self.move(dx, dy)

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt((dx**2) + (dy**2))


    def move(self, dx, dy):
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy

    def draw(self):
        if tcod.map_is_in_fov(fov_map, self.x, self.y):
            tcod.console_set_default_foreground(con, self.color)
            tcod.console_put_char(con, self.x, self.y, self.char, tcod.BKGND_NONE)

    def clear(self):
        tcod.console_put_char(con, self.x, self.y, ' ', tcod.BKGND_NONE)

def create_room(room):
    global map
    for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                map[x][y].blocked = False
                map[x][y].block_sight = False


def is_blocked (x, y):
    if map[x][y].blocked:
        return True

    for object in objects:
        if object.blocks and object.x ==x and object.y == y:
            return True

    return False

def message(new_msg, color = tcod.white):
    global messages
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    for line in new_msg_lines:
        if len(messages) == MSG_HEIGHT:
            del messages[0]
        messages.append((line, color))

def initialize_game():
    global con, panel, messages

    font_path = 'arial10x10.png'
    font_flags = tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD
    tcod.console_set_custom_font(font_path, font_flags)
    window_title = 'Dungeon Chef - a Saul Special'
    tcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, window_title, fullscreen)
    con = tcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
    tcod.sys_set_fps(LIMIT_FPS)

    panel = tcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
    messages = []

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    global panel
    bar_width = int(float(value) / maximum * total_width)

    tcod.console_set_default_background(panel, back_color)
    tcod.console_rect(panel, x, y, total_width, 1, False, tcod.BKGND_SCREEN)

    tcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        tcod.console_rect(panel, x, y, bar_width, 1, False, tcod.BKGND_SCREEN)

    tcod.console_set_default_foreground(panel, tcod.white)
    tcod.console_print_ex(panel, x + total_width//2, y, tcod.BKGND_NONE,
            tcod.CENTER, name + ': ' + str(value) + '/' + str (maximum))

def player_move_or_attack(dx, dy):
    global fov_recompute
    global objects

    x = player.x + dx
    y = player.y + dy

    target = None
    for object in objects:
        if object.fighter and object.x == x and object.y ==y:
            target = object
            break

    if target is not None:
        player.fighter.attack(target)
    else:
        player.move(dx, dy)
        fov_recompute = True

def handle_keys():
    global player
    global fov_recompute

    # REAL TIME PLAY
    key = tcod.console_check_for_keypress()

    if key.vk == tcod.KEY_ENTER and key.lalt:
        tcod.console_set_fullscreen(not tcod.console_is_fullscreen())
    elif key.vk == tcod.KEY_ESCAPE:
        return 'exit'

    if game_state == 'playing':
        if player.wait > 0:
            player.wait -= 1
            return
        if tcod.console_is_key_pressed(tcod.KEY_UP):
            player_move_or_attack(0, -1)
        elif tcod.console_is_key_pressed(tcod.KEY_DOWN):
            player_move_or_attack(0, 1)
        elif tcod.console_is_key_pressed(tcod.KEY_LEFT):
            player_move_or_attack(-1, 0)
        elif tcod.console_is_key_pressed(tcod.KEY_RIGHT):
            player_move_or_attack(1,0)
    else:
        return 'didnt-take-turn'



def make_map():
    global map, player

    map = [
            [Tile(True) for y in range(MAP_HEIGHT)]
            for x in range(MAP_WIDTH)
            ]

    rooms = []
    num_rooms = 0
    
    for r in range(MAX_ROOMS):
        w = tcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = tcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        x = tcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
        y = tcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)

        new_room = Rect(x, y, w, h)
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break
        if not failed:
            create_room(new_room)
            (new_x, new_y) = new_room.center()
            if num_rooms == 0:
                player.x = new_x
                player.y = new_y

            else:
                (prev_x, prev_y) = rooms[num_rooms-1].center()

                if tcod.random_get_int(0,0,1) == 1:
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)

            place_objects(new_room)
            rooms.append(new_room)
            num_rooms += 1


def create_h_tunnel(x1, x2, y):
    global map
    for x in range(min(x1,x2), max(x1, x2)+1):
            map[x][y].blocked = False
            map[x][y].block_sight = False


def create_v_tunnel(y1, y2, x):
    global map
    for y in range(min(y1,y2), max(y1, y2)+1):
            map[x][y].blocked=False
            map[x][y].block_sight = False



def render_all():
    global fov_map, color_dark_wall, color_light_wall
    global color_dark_ground, color_light_ground
    global fov_recompute, messages, panel

    if fov_recompute:
        fov_recompute = False
        tcod.map_compute_fov(fov_map, player.x, player.y,
                TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            visible = tcod.map_is_in_fov(fov_map, x, y)
            wall = map[x][y].block_sight
            if not visible:
                if map[x][y].explored:
                    if wall:
                        tcod.console_set_char_background(con, x, y, 
                                color_dark_wall, tcod.BKGND_SET)
                    else:
                        tcod.console_set_char_background(con, x, y, 
                                color_dark_ground, tcod.BKGND_SET)
            else:  
                if wall:
                    tcod.console_set_char_background(con, x, y, color_light_wall, 
                        tcod.BKGND_SET)
                else:
                    tcod.console_set_char_background(con, x, y, color_light_ground,
                        tcod.BKGND_SET)
                map[x][y].explored = True

                    
    for object in objects:
        if  tcod.map_is_in_fov(fov_map, object.x, object.y) and object != player:
            object.draw()
    player.draw()

    tcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    tcod.console_set_default_background(panel, tcod.black)
    tcod.console_clear(panel)
    y = 1
    for (line, color) in messages:
        tcod.console_set_default_foreground(panel, color)
        tcod.console_print_ex(panel, MSG_X, y, tcod.BKGND_NONE, tcod.LEFT, line)
        y +=1

    render_bar(1,1, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp,
            tcod.light_red, tcod.darker_red)
    tcod.console_blit(panel, 0,0,SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)




def place_objects(room):
    num_monsters = tcod.random_get_int(0, 0, MAX_ROOM_MONSTERS)

    for i in range (num_monsters):
        x = tcod.random_get_int(0, room.x1+1, room.x2-1)
        y = tcod.random_get_int(0, room.y1+1, room.y2-1)

        if tcod.random_get_int (0,0, 100) < 30:
            fighter_component = Fighter(hp=10, defense=0, power=3,
                    death_function = monster_death)
            ai_component = BasicMonster()

            monster = Object(x, y, 'D', tcod.desaturated_blue, 'dog',
                    blocks=True, fighter=fighter_component, ai=ai_component)
        else:
            fighter_component = Fighter(hp=6, defense=0, power=3,
                    death_function = monster_death)
            ai_component = BasicMonster()
            monster = Object(x, y, 'C', tcod.darker_gray, 'cat',
                    blocks=True, fighter=fighter_component, ai=ai_component)

        if not is_blocked(x, y):
            objects.append (monster)

def player_death(player):
    global game_state
    message ('You died!', tcod.red)
    game_state = 'dead'

    player.char = '%'
    player.color = tcod.dark_red


def monster_death(monster):
    message(monster.name.capitalize() + ' is dead!')
    monster.char = '%'
    monster.color = tcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = monster.name + ' corpse'
    monster.send_to_back()

def show_splashscreen():
    return


def start_game():
    global player, objects
    global game_state, player_action
    fighter_component = Fighter(hp=300, defense=2, power=5,
            death_function = player_death)
    player = Object(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, '@', tcod.white, 
            'player', blocks=True, fighter=fighter_component, speed=PLAYER_SPEED)

    objects = [player]

    make_map()
    
    global fov_map
    fov_map = tcod.map_new(MAP_WIDTH, MAP_HEIGHT)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            tcod.map_set_properties(fov_map, x, y, 
                    not map[x][y].block_sight, not map[x][y].blocked)

    global fov_recompute
    fov_recompute = True

    exit_game = False
    tcod.console_set_fullscreen(True)
    game_state = 'playing'
    player_action = None
    message('Welcome to Dungeon Chef - A Saul Special!', tcod.light_purple)
    while not tcod.console_is_window_closed() and not exit_game:
        render_all()
        tcod.console_flush()
        for object in objects:
            object.clear()
        
        player_action = handle_keys()
        if game_state == 'playing':
            for object in objects:
                if object.ai:
                    if object.wait > 0:
                        object.wait -= 1
                    else:
                        object.ai.take_turn()
        if game_state == 'dead':
            message('It\'s very sad. Press ESC to quit.....')

        if player_action == 'exit':
            if tcod.console_is_fullscreen():
                tcod.console_set_fullscreen(False)
            break

initialize_game()
show_splashscreen() # Saul should make me a splashscreen!
start_game()
